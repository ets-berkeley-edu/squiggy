"""
Copyright ©2022. The Regents of the University of California (Regents). All Rights Reserved.

Permission to use, copy, modify, and distribute this software and its documentation
for educational, research, and not-for-profit purposes, without fee and without a
signed licensing agreement, is hereby granted, provided that the above copyright
notice, this paragraph and the following two paragraphs appear in all copies,
modifications, and distributions.

Contact The Office of Technology Licensing, UC Berkeley, 2150 Shattuck Avenue,
Suite 510, Berkeley, CA 94720-1620, (510) 643-7201, otl@berkeley.edu,
http://ipira.berkeley.edu/industry-info for commercial licensing opportunities.

IN NO EVENT SHALL REGENTS BE LIABLE TO ANY PARTY FOR DIRECT, INDIRECT, SPECIAL,
INCIDENTAL, OR CONSEQUENTIAL DAMAGES, INCLUDING LOST PROFITS, ARISING OUT OF
THE USE OF THIS SOFTWARE AND ITS DOCUMENTATION, EVEN IF REGENTS HAS BEEN ADVISED
OF THE POSSIBILITY OF SUCH DAMAGE.

REGENTS SPECIFICALLY DISCLAIMS ANY WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE. THE
SOFTWARE AND ACCOMPANYING DOCUMENTATION, IF ANY, PROVIDED HEREUNDER IS PROVIDED
"AS IS". REGENTS HAS NO OBLIGATION TO PROVIDE MAINTENANCE, SUPPORT, UPDATES,
ENHANCEMENTS, OR MODIFICATIONS.
"""

import json
import os
import subprocess
import sys
import tempfile

from flask import current_app as app
from squiggy.lib.aws import get_s3_signed_url, is_s3_preview_url
from squiggy.models.whiteboard_element import WhiteboardElement


def to_png_file(whiteboard):
    base_dir = app.config['BASE_DIR']
    whiteboard_elements_file = tempfile.NamedTemporaryFile(suffix='.json').name
    with open(whiteboard_elements_file, mode='wt', encoding='utf-8') as f:
        elements = [w['element'] for w in whiteboard['whiteboardElements']]
        json.dump(elements, f)
    try:
        script = 'save_whiteboard_as_png.js'
        png_dir = os.path.dirname(os.path.realpath(whiteboard_elements_file))
        png_file = f'{png_dir}/whiteboard.png'
        subprocess.Popen(
            [
                app.config['NODE_EXECUTABLE'],
                f'{base_dir}/scripts/node_js/{script}',
                '-b',
                base_dir,
                '-w',
                whiteboard_elements_file,
                '-p',
                png_file,
            ],
            stdout=subprocess.PIPE,
        ).wait(timeout=200000)
        return png_file
    except OSError as e:
        app.logger.error(f"""
            OSError: {e.strerror}
            OSError number: {e.errno}
            OSError filename: {e.filename}
        """)
    except:  # noqa: E722
        app.logger.error(sys.exc_info()[0])


def is_ready_to_export(whiteboard_id):
    # TODO:
    elements = {
        'exportable': [],
        'pending': [],
        'errored': [],
    }
    asset_ids = []
    for whiteboard_element in WhiteboardElement.find_by_whiteboard_id(whiteboard_id=whiteboard_id):
        if not whiteboard_element.asset_id:
            element = whiteboard_element.element
            if element.src and is_s3_preview_url(element.src):
                element.src = get_s3_signed_url(element.src)
            elements['exportable'] = element
        elif whiteboard_element.asset_id not in asset_ids:
            asset_ids.append(whiteboard_element.asset_id)

    if not asset_ids:
        # No need to continue
        return
    # assets = Asset.get_assets(
    #     session=session,
    #     order_by='recent',
    #     offset=0,
    #     limit=50,
    #     filters={
    #
    #     },
    # )
    #   var assetOpts = {
    #     // Include deleted assets, since whiteboards may still refer to them.
    #     'paranoid': false,
    #     'where': {'id': assetIds}
    #   };
    #   DB.Asset.findAll(assetOpts).complete(function(err, assets) {
    #     async.each(whiteboard.whiteboardElements, function(whiteboardElement, done) {
    #       var assetId = whiteboardElement.asset_id;
    #       if (!assetId) {
    #         // Nothing to do if this element is not sourced from an asset.
    #         return done();
    #       } else {
    #         var matchingAsset = _.find(assets, {'id': assetId});
    #         if (!matchingAsset) {
    #           log.error({'whiteboardElement': whiteboardElement}, 'Asset not found for whiteboard element');
    #           elements.errored.push(whiteboardElement.id);
    #           return done();
    #         }
    #         var imageUrl = _.get(matchingAsset, 'image_url');
    #         var previewStatus = _.get(matchingAsset, 'preview_status');
    #         var width = _.get(matchingAsset, 'preview_metadata.image_width');
    #         // If we don't have complete preview data, mark the asset as lacking a preview.
    #         if (previewStatus !== 'done' || !imageUrl || !width) {
    #           log.warn({
    #             'whiteboard': whiteboard.id,
    #             'whiteboardElement': whiteboardElement.id,
    #             'asset': matchingAsset
    #           }, 'Whiteboard element lacks preview data for export');
    #           if (previewStatus === 'pending') {
    #             elements.pending.push(whiteboardElement.id);
    #           } else {
    #             elements.errored.push(whiteboardElement.id);
    #           }
    #           return done();
    #         } else {
    #           // The element has complete preview data and is exportable.
    #           elements.exportable.push(whiteboardElement.element);
    #           if (imageUrl !== whiteboardElement.element.src) {
    #             // If the whiteboard element has not been updated to reflect the preview, update it now.
    #             updateAssetPreviewForElement(whiteboardElement, imageUrl, width, done);
    #           } else {
    #             return done();
    #           }
    #         }
    #       }
    #     }, function(err) {
    #       if (err) {
    #         return callback(err);
    #       } else {
    #         return callback(null, elements);
    #       }
    #     });
    #   });
    return True

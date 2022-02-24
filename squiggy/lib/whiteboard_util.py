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

from squiggy.lib.aws import get_s3_signed_url, is_s3_preview_url
from squiggy.models.whiteboard_element import WhiteboardElement


def get_whiteboard_png_stream(session, whiteboard):
    if _check_element_exportability(session, whiteboard):
        pass
        # TODO:
        #     if (err) {
        #       log.error({
        #         'type': err,
        #         'whiteboard': whiteboard.id
        #       }, 'Whiteboard is not exportable');
        #       return callback({'code': 500, 'msg': 'There was an error exporting the whiteboard.'});
        #     } else if (!_.isEmpty(whiteboardElements.errored)) {
        #       return callback({
        #           'code': 400,
        #           'msg': 'The whiteboard could not be exported because one or more assets had a processing error. Remove blank assets to try again.'
        #       });
        #     } else if (!_.isEmpty(whiteboardElements.pending)) {
        #       return callback({
        #           'code': 400,
        #           'msg': 'Whiteboard could not be exported because some assets are still processing. Try again once processing is complete.'
        #       });
        #     }
        #     // Generating a PNG version of a whiteboard is a very CPU intensive process that can hold up the
        #     // Node.JS event loop. On top of that, fabric.js and its dependency node-canvas suffer from memory
        #     // leaks when importing images onto a Canvas. To avoid running out of memory or blocking the event loop,
        #     // a PNG version of a whiteboard is generated in a child process
        #     var childProcess = null;
        #     try {
        #       childProcess = spawn('node', ['../data/whiteboardToPng.js'], {
        #         'cwd': __dirname,
        #         'env': process.env
        #       });
        #     } catch (err) {
        #       log.error({
        #         'err': err,
        #         'whiteboard': whiteboard.id
        #       }, 'Could not spawn the whiteboardToPng child process');
        #       return callback({'code': 500, 'msg': 'Failed to convert the whiteboard to PNG'});
        #     }
        #     // If PNG generation for a single whiteboard takes more than 30 seconds, something isn't right.
        #     var childProcessTimeout = setTimeout(function() {
        #       childProcess.kill();
        #       log.error({'whiteboard': whiteboard.id}, 'The whiteboardToPng script timed out');
        #     }, 30000);
        #     // Feed the process the exportable elements
        #     var elements = JSON.stringify(whiteboardElements.exportable);
        #     childProcess.stdin.setEncoding = 'utf-8';
        #     childProcess.stdin.write(elements);
        #     childProcess.stdin.write('\n');
        #     // Buffer the PNG stream in memory
        #     var pngChunks = [];
        #     childProcess.stdout.on('data', function(chunk) {
        #       pngChunks.push(chunk);
        #     });
        #     // Log the error message the child process generates
        #     childProcess.stderr.on('data', function(data) {
        #       log.error({
        #           'data': data.toString('utf-8'),
        #           'whiteboard': whiteboard.id
        #         }, 'Error output when converting a whiteboard to PNG');
        #     });
        #     // Once the PNG has been generated (or the script fails), return to the caller
        #     childProcess.on('close', function(code) {
        #       clearTimeout(childProcessTimeout);
        #       if (code !== 0) {
        #         log.error({
        #           'code': code,
        #           'whiteboard': whiteboard.id
        #         }, 'The whiteboardToPng script exited with an unexpected error code');
        #         return callback({'code': 500, 'msg': 'Failed to convert the whiteboard to PNG'});
        #       }
        #       // The last chunk contains the dimensions object, set off by a newline.
        #       var lastPngChunk = pngChunks.pop();
        #       var lastPngChunkLines = lastPngChunk.toString('utf8').split("\n");
        #       var dimensionsData = lastPngChunkLines.pop();
        #       // Image data may have been buffered in the same chunk as the dimensions object, in which case we
        #       // should restore it to pngChunks.
        #       if (lastPngChunkLines.length) {
        #         var buffer = new Buffer(lastPngChunkLines.join("\n"), 'utf8');
        #         pngChunks.push(buffer);
        #       }
        #       try {
        #         var dimensions = JSON.parse(dimensionsData);
        #       } catch (err) {
        #         return callback({'code': 500, 'msg': 'Failed to parse the dimensions data'});
        #       }
        #       return callback(null, Buffer.concat(pngChunks), dimensions);


def _check_element_exportability(session, whiteboard):
    pass
    # TODO:
    elements = {
        'exportable': [],
        'pending': [],
        'errored': [],
    }
    asset_ids = []
    for whiteboard_element in WhiteboardElement.find_by_whiteboard_id(whiteboard_id=whiteboard.id):
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

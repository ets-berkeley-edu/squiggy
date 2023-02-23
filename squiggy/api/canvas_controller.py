"""
Copyright ©2023. The Regents of the University of California (Regents). All Rights Reserved.

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

from flask import current_app as app, request, Response
from squiggy.lib.lti import get_tool_metadata, TOOL_ID_ASSET_LIBRARY, TOOL_ID_ENGAGEMENT_INDEX, TOOL_ID_IMPACT_STUDIO, TOOL_ID_WHITEBOARDS


@app.route('/lti/cartridge/asset_library.xml')
def asset_library_xml():
    return Response(
        _get_lti_cartridge_xml(
            host=request.headers['Host'],
            tool_id=TOOL_ID_ASSET_LIBRARY,
        ),
        mimetype='application/xml',
    )


@app.route('/lti/cartridge/engagement_index.xml')
def engagement_index_xml():
    return Response(
        _get_lti_cartridge_xml(
            host=request.headers['Host'],
            tool_id=TOOL_ID_ENGAGEMENT_INDEX,
        ),
        mimetype='application/xml',
    )


@app.route('/lti/cartridge/impact_studio.xml')
def impact_studio_xml():
    return Response(
        _get_lti_cartridge_xml(
            host=request.headers['Host'],
            tool_id=TOOL_ID_IMPACT_STUDIO,
        ),
        mimetype='application/xml',
    )


@app.route('/lti/cartridge/whiteboards.xml')
def whiteboards_xml():
    return Response(
        _get_lti_cartridge_xml(
            host=request.headers['Host'],
            tool_id=TOOL_ID_WHITEBOARDS,
        ),
        mimetype='application/xml',
    )


def _get_lti_cartridge_xml(host, tool_id):
    tool_metadata = get_tool_metadata(host=host, tool_id=tool_id)
    launch_url = tool_metadata['launch_url']
    title = tool_metadata['title']
    return f"""<?xml version="1.0" encoding="UTF-8"?>
        <cartridge_basiclti_link
          xmlns="http://www.imsglobal.org/xsd/imslticc_v1p0"
          xmlns:blti = "http://www.imsglobal.org/xsd/imsbasiclti_v1p0"
          xmlns:lticm ="http://www.imsglobal.org/xsd/imslticm_v1p0"
          xmlns:lticp ="http://www.imsglobal.org/xsd/imslticp_v1p0"
          xmlns:xsi = "http://www.w3.org/2001/XMLSchema-instance"
          xsi:schemaLocation = "
            http://www.imsglobal.org/xsd/imslticc_v1p0 http://www.imsglobal.org/xsd/lti/ltiv1p0/imslticc_v1p0.xsd
            http://www.imsglobal.org/xsd/imsbasiclti_v1p0 http://www.imsglobal.org/xsd/lti/ltiv1p0/imsbasiclti_v1p0.xsd
            http://www.imsglobal.org/xsd/imslticm_v1p0 http://www.imsglobal.org/xsd/lti/ltiv1p0/imslticm_v1p0.xsd
            http://www.imsglobal.org/xsd/imslticp_v1p0 http://www.imsglobal.org/xsd/lti/ltiv1p0/imslticp_v1p0.xsd">
          <blti:title>{title}</blti:title>
          <blti:description>{tool_metadata['description']}</blti:description>
          <blti:launch_url>{launch_url}</blti:launch_url>
          <blti:extensions platform="canvas.instructure.com">
            <lticm:property name="tool_id">{tool_id}</lticm:property>
            <lticm:property name="privacy_level">public</lticm:property>
            <lticm:options name="course_navigation">
              <lticm:property name="url">{launch_url}</lticm:property>
              <lticm:property name="text">{title}</lticm:property>
              <lticm:property name="visibility">public</lticm:property>
              <lticm:property name="default">disabled</lticm:property>
              <lticm:property name="enabled">false</lticm:property>
              <lticm:options name="custom_fields">
                <lticm:property name="external_tool_url">$Canvas.externalTool.url</lticm:property>
              </lticm:options>
            </lticm:options>
          </blti:extensions>
          <cartridge_bundle identifierref="BLTI001_Bundle"/>
          <cartridge_icon identifierref="BLTI001_Icon"/>
        </cartridge_basiclti_link>
    """

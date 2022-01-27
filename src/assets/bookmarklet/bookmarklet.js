/**
 * Copyright ©2022. The Regents of the University of California (Regents). All Rights Reserved.
 *
 * Permission to use, copy, modify, and distribute this software and its documentation
 * for educational, research, and not-for-profit purposes, without fee and without a
 * signed licensing agreement, is hereby granted, provided that the above copyright
 * notice, this paragraph and the following two paragraphs appear in all copies,
 * modifications, and distributions.
 *
 * Contact The Office of Technology Licensing, UC Berkeley, 2150 Shattuck Avenue,
 * Suite 510, Berkeley, CA 94720-1620, (510) 643-7201, otl@berkeley.edu,
 * http://ipira.berkeley.edu/industry-info for commercial licensing opportunities.
 *
 * IN NO EVENT SHALL REGENTS BE LIABLE TO ANY PARTY FOR DIRECT, INDIRECT, SPECIAL,
 * INCIDENTAL, OR CONSEQUENTIAL DAMAGES, INCLUDING LOST PROFITS, ARISING OUT OF
 * THE USE OF THIS SOFTWARE AND ITS DOCUMENTATION, EVEN IF REGENTS HAS BEEN ADVISED
 * OF THE POSSIBILITY OF SUCH DAMAGE.
 *
 * REGENTS SPECIFICALLY DISCLAIMS ANY WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
 * IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE. THE
 * SOFTWARE AND ACCOMPANYING DOCUMENTATION, IF ANY, PROVIDED HEREUNDER IS PROVIDED
 * "AS IS". REGENTS HAS NO OBLIGATION TO PROVIDE MAINTENANCE, SUPPORT, UPDATES,
 * ENHANCEMENTS, OR MODIFICATIONS.
 */

(function() {

  // Create an iFrame that will overlay the existing page. This will appear to load the bookmarklet content
  // inside of the page, but in reality it will just be an iFrame on top of the page. This will give us
  // a lot more control over the behavior and styling of the Bookmarklet content and removes the potential for
  // clashes with the parent page.
  const iFrame = document.createElement('iframe')
  iFrame.id = 'squiggy-iframe'
  iFrame.style = {
    ...(iFrame.style || {}),
    ...{
      position: 'fixed',
      top: '0px',
      left: '0px',
      bottom: '0px',
      right: '0px',
      width: '100%',
      height: '100%',
      border: 'none',
      margin: '0',
      padding: '0',
      overflow: 'hidden',
      zIndex: '2147483647'
    }
  }
  // Add the iFrame to the page and load the appropriate libraries containing the Bookmarklet's working code
  document.body.appendChild(iFrame)
  const baseUrl = window.squiggy.baseUrl
  const html = `
    <!DOCTYPE html>
    <html lang="en">
      <head>
        <meta charset="utf-8">
        <meta http-equiv="X-UA-Compatible" content="IE=edge">
        // Note that these dependencies are parsed by the production build. Take caution
        // when adjusting the formatting or when adding new dependencies
        <link href="${baseUrl}/lib/bootstrap/dist/css/bootstrap.css" rel="stylesheet">
        <link href="${baseUrl}/assets/css/main.css" rel="stylesheet">
        <link href="${baseUrl}/assets/css/bookmarklet.css" rel="stylesheet">
        <script src="${baseUrl}/lib/jquery/dist/jquery.js"></script>
        <script src="${baseUrl}/lib/lodash/lodash.js"></script>
        <script src="${baseUrl}/lib/bootstrap/dist/js/bootstrap.js"></script>
        <script src="${baseUrl}/lib/remarkable-bootstrap-notify/dist/bootstrap-notify.js"></script>
      </head>
      <body>
        <script src="${baseUrl}/assets/js/bookmarklet.js"></script>
      </body>
    </html>
  `
  iFrame.contentWindow.document.open()
  iFrame.contentWindow.document.write(html)
  iFrame.contentWindow.document.close()
}())

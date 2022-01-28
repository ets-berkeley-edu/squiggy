/**
 * Copyright ©2020. The Regents of the University of California (Regents). All Rights Reserved.
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

  const e = document.createElement('iframe')
  e.id = 'squiggy-iframe'
  e.style.position = 'fixed'
  e.style.top = '0px'
  e.style.left = '0px'
  e.style.bottom = '0px'
  e.style.right = '0px'
  e.style.width = '100%'
  e.style.height = '100%'
  e.style.border = 'none'
  e.style.margin = 0
  e.style.padding = 0
  e.style.overflow = 'hidden'
  e.style.zIndex = 2147483647

  document.body.appendChild(e)

  e.contentWindow.document.open()
  e.contentWindow.document.write(`
    <!DOCTYPE html>
    <html lang="en">
      <head>
        <meta charset="utf-8">
        <meta http-equiv="X-UA-Compatible" content="IE=edge">
        <link href="{apiBaseUrl}/lib/bootstrap/dist/css/bootstrap.css" rel="stylesheet">
        <link href="{apiBaseUrl}/assets/css/main.css" rel="stylesheet">
        <link href="{apiBaseUrl}/assets/css/bookmarklet.css" rel="stylesheet">
        <script src="{apiBaseUrl}/lib/jquery/dist/jquery.js"></script>
        <script src="{apiBaseUrl}/lib/lodash/lodash.js"></script>
        <script src="{apiBaseUrl}/lib/bootstrap/dist/js/bootstrap.js"></script>
        <script src="{apiBaseUrl}/lib/remarkable-bootstrap-notify/dist/bootstrap-notify.js"></script>
      </head>
      <body>
        <script src="{apiBaseUrl}/bookmarklet/render.js"></script>
      </body>
    </html>
  `)
  e.contentWindow.document.close()
}())

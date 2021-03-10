"""
Copyright ©2021. The Regents of the University of California (Regents). All Rights Reserved.

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

from flask import current_app as app, request
from flask_login import current_user, login_required
from squiggy.api.errors import BadRequestError, ResourceNotFoundError
from squiggy.lib.http import tolerant_jsonify
from squiggy.models.asset import Asset
from squiggy.models.category import Category
from squiggy.models.user import User


@app.route('/api/asset/<asset_id>')
@login_required
def get_asset(asset_id):
    asset = Asset.find_by_id(asset_id=asset_id)
    if asset:
        return tolerant_jsonify(asset.to_api_json())
    else:
        raise ResourceNotFoundError(f'No asset found with id: {asset_id}')


@app.route('/api/asset/upload', methods=['POST'])
@login_required
def upload():
    file_upload = _get_upload_from_http_post()
    asset = Asset.create(
        asset_type='file',
        course_id=current_user.course.id,
        title=file_upload['name'],
        users=[User.find_by_id(current_user.get_id())],
    )
    return tolerant_jsonify(asset.to_api_json())


@app.route('/api/assets', methods=['POST'])
@login_required
def get_assets():
    params = request.get_json()
    app.logger.info('ARHD')
    app.logger.info(request.args)
    sort = _get(request.args, 'sort', None)
    offset = params.get('offset')
    limit = params.get('limit')
    filters = {
        'asset_type': _get(request.args, 'assetType', None),
        'category_id': _get(request.args, 'categoryId', None),
        'has_comments': _get(request.args, 'hasComments', None),
        'has_likes': _get(request.args, 'hasLikes', None),
        'has_views': _get(request.args, 'hasViews', None),
        'keywords': _get(request.args, 'keywords', None),
        'order_by': _get(request.args, 'orderBy', 'recent'),
        'owner_id': _get(request.args, 'userId', None),
        'section_id': _get(request.args, 'sectionId', None),
    }
    results = Asset.get_assets(session=current_user, sort=sort, offset=offset, limit=limit, filters=filters)
    return tolerant_jsonify(results)


@app.route('/api/asset/create', methods=['POST'])
@login_required
def create_asset():
    params = request.get_json()
    asset_type = params.get('type')
    category_id = params.get('categoryId')
    description = params.get('description')
    source = params.get('source')
    url = params.get('url')
    title = params.get('title', url)
    visible = params.get('visible', True)
    if not asset_type or not title or not url:
        raise BadRequestError('Asset creation requires category, title, and url.')

    if not current_user.course:
        raise BadRequestError('Course data not found')

    asset = Asset.create(
        asset_type=asset_type,
        categories=Category.get_categories_by_id([category_id]) if category_id else None,
        course_id=current_user.course.id,
        description=description,
        source=source,
        title=title,
        url=url,
        users=[User.find_by_id(current_user.get_id())],
        visible=visible,
    )
    return tolerant_jsonify(asset.to_api_json())


@app.route('/api/asset/update', methods=['POST'])
@login_required
def update_asset():
    params = request.get_json()
    asset_id = params.get('assetId')
    category_id = params.get('categoryId')
    description = params.get('description')
    title = params.get('title')
    if not asset_id or not title:
        raise BadRequestError('Asset creation requires category and title.')
    asset = Asset.update(
        asset_id=asset_id,
        categories=Category.get_categories_by_id([category_id]) if category_id else None,
        description=description,
        title=title,
    )
    return tolerant_jsonify(asset.to_api_json())


def _get(_dict, key, default_value=None):
    return _dict[key] if key in _dict else default_value


def _load_json(path):
    try:
        file = open(f"{app.config['BASE_DIR']}/{path}")
        return json.load(file)
    except (FileNotFoundError, KeyError, TypeError):
        return None


def _hot_100_of_1973():
    return {
        {'title': 'Tie a Yellow Ribbon Round the Ole Oak Tree', 'artist': 'Tony Orlando and Dawn'},
        {'title': 'Bad, Bad Leroy Brown', 'artist': 'Jim Croce'},
        {'title': 'Killing Me Softly with His Song', 'artist': 'Roberta Flack'},
        {'title': 'Let\'s Get It On', 'artist': 'Marvin Gaye'},
        {'title': 'My Love', 'artist': 'Paul McCartney & Wings'},
        {'title': 'Why Me', 'artist': 'Kris Kristofferson'},
        {'title': 'Crocodile Rock', 'artist': 'Elton John'},
        {'title': 'Will It Go Round in Circles', 'artist': 'Billy Preston'},
        {'title': 'You\'re So Vain', 'artist': 'Carly Simon'},
        {'title': 'Touch Me in the Morning', 'artist': 'Diana Ross'},
        {'title': 'The Night the Lights Went Out in Georgia', 'artist': 'Vicki Lawrence'},
        {'title': 'Playground in My Mind', 'artist': 'Clint Holmes'},
        {'title': 'Brother Louie', 'artist': 'Stories'},
        {'title': 'Delta Dawn', 'artist': 'Helen Reddy'},
        {'title': 'Me and Mrs. Jones', 'artist': 'Billy Paul'},
        {'title': 'Frankenstein', 'artist': 'The Edgar Winter Group'},
        {'title': 'Drift Away', 'artist': 'Dobie Gray'},
        {'title': 'Little Willy', 'artist': 'Sweet'},
        {'title': 'You Are the Sunshine of My Life', 'artist': 'Stevie Wonder'},
        {'title': 'Half-Breed', 'artist': 'Cher'},
        {'title': 'That Lady', 'artist': 'The Isley Brothers'},
        {'title': 'Pillow Talk', 'artist': 'Sylvia Robinson'},
        {'title': 'We\'re an American Band', 'artist': 'Grand Funk Railroad'},
        {'title': 'Right Place Wrong Time', 'artist': 'Dr. John'},
        {'title': 'Wildflower', 'artist': 'Skylark'},
        {'title': 'Superstition', 'artist': 'Stevie Wonder'},
        {'title': 'Loves Me Like a Rock', 'artist': 'Paul Simon'},
        {'title': 'The Morning After', 'artist': 'Maureen McGovern'},
        {'title': 'Rocky Mountain High', 'artist': 'John Denver'},
        {'title': 'Stuck in the Middle with You', 'artist': 'Stealers Wheel'},
        {'title': 'Shambala', 'artist': 'Three Dog Night'},
        {'title': 'Love Train', 'artist': 'The O\'Jays'},
        {'title': 'I\'m Gonna Love You Just a Little More Baby', 'artist': 'Barry White'},
        {'title': 'Say, Has Anybody Seen My Sweet Gypsy Rose', 'artist': 'Tony Orlando and Dawn'},
        {'title': 'Keep on Truckin\'', 'artist': 'Eddie Kendricks'},
        {'title': 'Danny\'s Song', 'artist': 'Anne Murray'},
        {'title': 'Dancing in the Moonlight', 'artist': 'King Harvest'},
        {'title': 'Monster Mash', 'artist': 'Bobby Pickett'},
        {'title': 'Natural High', 'artist': 'Bloodstone'},
        {'title': 'Diamond Girl', 'artist': 'Seals and Crofts'},
        {'title': 'Long Train Runnin\'', 'artist': 'The Doobie Brothers'},
        {'title': 'Give Me Love (Give Me Peace on Earth)', 'artist': 'George Harrison'},
        {'title': 'If You Want Me to Stay', 'artist': 'Sly & the Family Stone'},
        {'title': 'Daddy\'s Home', 'artist': 'Jermaine Jackson'},
        {'title': 'Neither One of Us (Wants to Be the First to Say Goodbye)', 'artist': 'Gladys Knight & the Pips'},
        {'title': 'I\'m Doin\' Fine Now', 'artist': 'New York City'},
        {'title': 'Could It Be I\'m Falling in Love', 'artist': 'The Spinners'},
        {'title': 'Daniel', 'artist': 'Elton John'},
        {'title': 'Midnight Train to Georgia', 'artist': 'Gladys Knight & the Pips'},
        {'title': 'Smoke on the Water', 'artist': 'Deep Purple'},
        {'title': 'The Cover of the Rolling Stone', 'artist': 'Dr. Hook & The Medicine Show'},
        {'title': 'Behind Closed Doors', 'artist': 'Charlie Rich'},
        {'title': 'Your Mama Don\'t Dance', 'artist': 'Loggins and Messina'},
        {'title': 'Feelin\' Stronger Every Day', 'artist': 'Chicago'},
        {'title': 'The Cisco Kid', 'artist': 'War'},
        {'title': 'Live and Let Die', 'artist': 'Paul McCartney & Wings'},
        {'title': 'Oh, Babe, What Would You Say?', 'artist': 'Hurricane Smith'},
        {'title': 'I Believe in You (You Believe in Me)', 'artist': 'Johnnie Taylor'},
        {'title': 'Sing', 'artist': 'The Carpenters'},
        {'title': 'Ain\'t No Woman (Like the One I\'ve Got)', 'artist': 'The Four Tops'},
        {'title': 'Dueling Banjos', 'artist': 'Eric Weissberg & Steve Mandell'},
        {'title': 'Higher Ground', 'artist': 'Stevie Wonder'},
        {'title': 'Here I Am (Come and Take Me)', 'artist': 'Al Green'},
        {'title': 'My Maria', 'artist': 'B.W. Stevenson'},
        {'title': 'Superfly', 'artist': 'Curtis Mayfield'},
        {'title': 'Last Song', 'artist': 'Edward Bear'},
        {'title': 'Get Down', 'artist': 'Gilbert O\'Sullivan'},
        {'title': 'Reelin\' in the Years', 'artist': 'Steely Dan'},
        {'title': 'Hocus Pocus', 'artist': 'Focus'},
        {'title': 'Yesterday Once More', 'artist': 'The Carpenters'},
        {'title': 'Boogie Woogie Bugle Boy', 'artist': 'Bette Midler'},
        {'title': 'Clair', 'artist': 'Gilbert O\'Sullivan'},
        {'title': 'Do It Again', 'artist': 'Steely Dan'},
        {'title': 'Kodachrome', 'artist': 'Paul Simon'},
        {'title': 'Why Can\'t We Live Together', 'artist': 'Timmy Thomas'},
        {'title': 'Do You Wanna Dance?', 'artist': 'Bette Midler'},
        {'title': 'So Very Hard to Go', 'artist': 'Tower of Power'},
        {'title': 'Rockin\' Pneumonia and the Boogie Woogie Flu', 'artist': 'Johnny Rivers'},
        {'title': 'Ramblin\' Man', 'artist': 'The Allman Brothers Band'},
        {'title': 'Masterpiece', 'artist': 'The Temptations'},
        {'title': 'Peaceful', 'artist': 'Helen Reddy'},
        {'title': 'One of a Kind (Love Affair)', 'artist': 'The Spinners'},
        {'title': 'Funny Face', 'artist': 'Donna Fargo'},
        {'title': 'Funky Worm', 'artist': 'Ohio Players'},
        {'title': 'Angie', 'artist': 'The Rolling Stones'},
        {'title': 'Jambalaya (On the Bayou)', 'artist': 'Blue Ridge Rangers'},
        {'title': 'Don\'t Expect Me to Be Your Friend', 'artist': 'Lobo'},
        {'title': 'Break Up to Make Up', 'artist': 'The Stylistics'},
        {'title': 'Daisy a Day', 'artist': 'Jud Strunk'},
        {'title': 'Also Sprach Zarathustra (2001)', 'artist': 'Deodato'},
        {'title': 'Stir It Up', 'artist': 'Johnny Nash'},
        {'title': 'Money', 'artist': 'Pink Floyd'},
        {'title': 'Gypsy Man', 'artist': 'War'},
        {'title': 'The World Is a Ghetto', 'artist': 'War'},
        {'title': 'Yes We Can Can', 'artist': 'The Pointer Sisters'},
        {'title': 'Free Ride', 'artist': 'The Edgar Winter Group'},
        {'title': 'Space Oddity', 'artist': 'David Bowie'},
        {'title': 'It Never Rains in Southern California', 'artist': 'Albert Hammond'},
        {'title': 'The Twelfth of Never', 'artist': 'Donny Osmond'},
        {'title': 'Papa Was a Rollin\' Stone', 'artist': 'The Temptations'},
    }


def _get_upload_from_http_post():
    request_files = request.files
    file = request_files.get('file[0]')
    if not file:
        raise BadRequestError('request.files is empty')

    filename = file.filename and file.filename.strip()
    if not filename:
        raise BadRequestError(f'Invalid file: {filename}')

    return {
        'name': filename.rsplit('/', 1)[-1],
        'byte_stream': file.read(),
    }

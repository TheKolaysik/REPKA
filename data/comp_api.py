import flask
from flask import jsonify, make_response, request

from . import db_session
from .components import Components

blueprint = flask.Blueprint(
    'comp_api',
    __name__,
    template_folder='templates'
)


@blueprint.route('/api/comps/<int:comp_id>', methods=['GET'])
def get_one_comp(comp_id):
    db_sess = db_session.create_session()
    comps = db_sess.query(Components).get(comp_id)
    if not comps:
        return jsonify({'error': 'Not found'})
    return jsonify(
        {
            'components': comps.to_dict(only=(
                'title', 'type', 'about', 'datasheet'))
        }
    )


@blueprint.route('/api/comps', methods=['POST'])
def create_comp():
    if not request.json:
        return jsonify({'error': 'Empty request'})
    elif not all(key in request.json for key in
                 ['title', 'type', 'about', 'datasheet']):
        return jsonify({'error': 'Bad request'})
    db_sess = db_session.create_session()
    comps = Components(
        title=request.json['title'],
        type=request.json['type'],
        about=request.json['about'],
        datasheet=request.json['datasheet']
    )
    db_sess.add(comps)
    db_sess.commit()
    return jsonify({'success': 'OK'})


@blueprint.route('/api/comps/<int:comp_id>', methods=['DELETE'])
def delete_news(comp_id):
    db_sess = db_session.create_session()
    comps = db_sess.query(Components).get(comp_id)
    if not comps:
        return jsonify({'error': 'Not found'})
    db_sess.delete(comps)
    db_sess.commit()
    return jsonify({'success': 'OK'})




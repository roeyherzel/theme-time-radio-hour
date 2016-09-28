from archive.common.utils import limit_query
from archive.common.schemas import TrackSchema
from archive.models import *

from flask_restful import Resource, abort, reqparse, marshal_with

from sqlalchemy import desc
from sqlalchemy.orm.exc import NoResultFound


class ApiTrack(Resource):

    @marshal_with(TrackSchema)
    def get(self, track_id):
        return Tracks.query.get(track_id)


class ApiTracksArtists(Resource):

    def post(self, track_id):
        parser = reqparse.RequestParser()
        parser.add_argument('id')
        args = parser.parse_args()

        artist_id = args.id

        try:
            myTrack = TracksArtists.query.filter_by(track_id=track_id, artist_id=artist_id).one()

        except NoResultFound as err:
            msg = "didn't find pending resource with track_id({}) and artist_id({})".format(track_id, artist_id)
            print("match - {}".format(msg))
            abort(404, message=msg)

        myTrack.status = Status.getIdByName('matched')
        TracksArtists.update(myTrack)
        print("match - updated track_id({}) -> artist_id({}): status(matched)".format(artist_id, track_id))

        TracksArtists.query.filter_by(track_id=track_id) \
                           .filter(TracksArtists.status != Status.getIdByName('matched')) \
                           .delete()

        print("match - deleting all other pending")
        db.session.commit()
        print("match - commited")

        return artist_id, 201


class ApiTracksReleases(Resource):

    def post(self, track_id):
        parser = reqparse.RequestParser()
        parser.add_argument('id')
        args = parser.parse_args()

        release_id = args.id

        try:
            tracks_release = TracksReleases.query.filter_by(track_id=track_id, release_id=release_id).one()

        except NoResultFound as err:
            msg = "didn't find pending resource with track_id({}) and release_id({})".format(track_id, release_id)
            print("match - {}".format(msg))
            abort(404, message=msg)

        # set matched status
        tracks_release.status = Status.getIdByName('matched')
        TracksReleases.update(tracks_release)
        print("match - updated release_id({}) -> track_id({}): status(matched)".format(track_id, release_id))

        # remove all pending
        TracksReleases.query.filter_by(track_id=track_id) \
                            .filter(TracksReleases.status != Status.getIdByName('matched')) \
                            .delete()

        print("match - deleting all other pending")
        db.session.commit()
        print("match - commited")

        # Attach matched releases songs to pending track songs
        for s in Songs.query.filter_by(release_id=release_id):
            print("match- adding song_id({}) -> track_id({}): status(pending)".format(s.id, track_id))
            TracksSongs.create(TracksSongs(track_id=track_id, song_id=s.id, status=Status.getIdByName('pending')))

        return release_id, 201


class ApiTracksSongs(Resource):

    def post(self, track_id):
        parser = reqparse.RequestParser()
        parser.add_argument('id')
        args = parser.parse_args()

        song_id = args.id

        try:
            myTrack = TracksSongs.query.filter_by(track_id=track_id, song_id=song_id).one()

        except NoResultFound as err:
            msg = "didn't find pending resource with track_id({}) and song_id({})".format(track_id, song_id)
            print("match - {}".format(msg))
            abort(404, message=msg)

        myTrack.status = Status.getIdByName('matched')
        TracksSongs.update(myTrack)
        print("match - updated track_id({}) -> song_id({}): status(matched)".format(song_id, track_id))

        TracksSongs.query.filter_by(track_id=track_id) \
                         .filter(TracksSongs.status != Status.getIdByName('matched')) \
                         .delete()

        print("match - deleting all other pending")
        db.session.commit()
        print("match - commited")

        return song_id, 201
import { Artists } from '../js/app';


! function () {
    const artistId = $('#page header h1').attr('data-artist-id');
    const artistName = $('#page header h1').attr('data-artist-lastfm');

    Artists.renderTracks(artistId);
    Artists.renderInfo(artistName)
}();
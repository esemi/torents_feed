document.addEventListener('DOMContentLoaded', function() {

    let favorites_offset = 0;
    let unsort_limit = 15;

    fetch(new Request('/stat.json'))
    .then(function(response) { return response.json(); })
    .then(function(response_json) {
        stat = response_json['stat']
        document.querySelector('#stat_last_update').innerHTML = new Date(stat['last_update'] * 1000).toISOString()
        document.querySelector('#stat_total_bookmarks').innerHTML = stat['total_bookmarks']
        document.querySelector('#stat_total_torrents').innerHTML = stat['total_torrents']
        document.querySelector('#stat_last_bookmark').innerHTML = stat['last_bookmark']
        document.querySelector('#stat_last_torrent').innerHTML = stat['last_torrent']
    });

    function loadBookmarks(type, limit, offset) {
        fetch(new Request(`/bookmarks/${type}.json?limit=${limit}`))
        .then(function(response) { return response.json(); })
        .then(function(response_json) {
            let container = document.querySelector(`#${type} ul`);

            let bookmarks = response_json['bookmarks'];
            console.log(bookmarks, container);

            bookmarks.forEach(function(el, index, array) {
                let li = document.createElement('li');
                li.setAttribute('data-js-bookmark', el._id);
                li.appendChild(document.createTextNode(el._id));
                container.appendChild(li)
            });
        });
    }


    loadBookmarks('unsort', unsort_limit, 0);

//    document.addEventListener('click', function(e) {
//       if (e.target.matches('#unsort [data-js="load-button"]')) {
//           loadBookmarks('unsort', unsort_limit, 0);
//       }
//    }, false);

});

(function () {

    var app = window.app = window.app || {};

    (function () {
        app.load_data_get = function (url, params, success_callback) {
            $.ajax({
                url: url,
                dataType: 'json',
                data: params,
                success: function (data) {

                    success_callback(data);
                },
                cache: false
            });
        };

        app.load_data_post = function (url, params, change_callback) {

            $.ajax({
                url: url,
                dataType: 'json',
                data: params,
                type: 'POST',
                success: function (data) {

                    change_callback(data);
                },
                cache: false
            });
        };

    })();

})();


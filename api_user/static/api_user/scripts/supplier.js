var map_obj = {
    _map: {},
    _marker: {},
    _geocoder: {},
    init: function (initialPosition, defaultPosition) {
        var self = this;
        var markerIsSet = initialPosition;
        if (!markerIsSet) initialPosition = defaultPosition;

        self._map = new google.maps.Map(
            document.getElementById('map'), {
                zoom: 12,
                center: initialPosition,
                mapTypeId: google.maps.MapTypeId.ROADMAP
            });


        self._marker = new google.maps.Marker({
            position: initialPosition,
            map: self._map,
            draggable: true
        });

        self._geocoder = new google.maps.Geocoder;

        if (!markerIsSet) {
            var infoWindow = new google.maps.InfoWindow;
            // Try HTML5 geolocation.
            if (navigator.geolocation) {
                navigator.geolocation.getCurrentPosition(function (position) {
                    var pos = {
                        lat: position.coords.latitude,
                        lng: position.coords.longitude
                    };
                    infoWindow.setPosition(pos);
                    infoWindow.setContent('Location found!');
                    infoWindow.open(self._map);
                    self._map.setZoom(17);
                    setTimeout(function () {
                        infoWindow.close();
                        // change marker position
                        var latlng = new google.maps.LatLng(pos.lat, pos.lng);
                        self._marker.setPosition(latlng);
                    }, 1500);
                    self._map.setCenter(pos);
                }, function () {
                    self._handleLocationError(true, infoWindow, self._map.getCenter());
                });
            } else {
                // Browser doesn't support Geolocation
                self._handleLocationError(false, infoWindow, self._map.getCenter());
            }
        }
    },

    getAddress: function (func) {
        var self = this;
        var address = null;
        self._geocoder.geocode({'location': self.getMarkerPosition()}, function (results, status) {
        console.info(results[0]);
        if (status === 'OK') {
                if (results[0]) {
                    address = self._formatAddress(results[0]);
                    func(address);
                } else {
                    console.warn('No results found');
                }
            } else {
                console.warn('Geocoder failed due to: ' + status);
            }
        });
    },

    _formatAddress: function (adrObj) {
        adrObj['address_components'] = adrObj['address_components'].reverse();
        return {
            'place_id': adrObj['place_id'],
            'full_address_array': adrObj['address_components'],
            'postal_code': getValue(adrObj['address_components'], [0, 'short_name'], '-'),
            'country': getValue(adrObj['address_components'], [1, 'short_name'], '-'), //country
            'county': getValue(adrObj['address_components'], [2, 'long_name'], '-'), //county
            'city': getValue(adrObj['address_components'], [3, 'long_name'], '-'), //city
            'neighbourhood': getValue(adrObj['address_components'], [4, 'long_name'], '-'),   //neighbourhood
            'street': getValue(adrObj['address_components'], [5, 'long_name'], '-'),   //street
            'street_no': getValue(adrObj['address_components'], [6, 'short_name'], '-')   //street no
        };
        
        function getValue(array, keyArr, default_value) {
            if (keyArr[0] in array) {
                if (keyArr[1] in array[keyArr[0]]) {
                    return array[keyArr[0]][keyArr[1]];
                }
            }
            return default_value;
        }
    },

    _handleLocationError: function (browserHasGeolocation, infoWindow, pos) {
        infoWindow.setPosition(pos);
        infoWindow.setContent(browserHasGeolocation ?
            'Error: The Geolocation service failed.' :
            'Error: Your browser doesn\'t support geolocation.');
        infoWindow.open(self._map);
    },

    setDragFunction: function (dragFunc) {
        var self = this;

        self._marker.addListener('dragend', dragFunc)
    },

    getMarkerPosition: function () {
        var self = this;
        return {
            'lat': self._marker.getPosition().lat(),
            'lng': self._marker.getPosition().lng()
        }
    }
};

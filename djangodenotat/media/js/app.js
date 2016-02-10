'use strict';

angular.module('denotatApp', [
    'ui.bootstrap',                 // Ui Bootstrap
    'bootstrap.fileField'
])
.config(function ($httpProvider, $interpolateProvider) {
    $interpolateProvider.startSymbol('{$');
    $interpolateProvider.endSymbol('$}');

    $httpProvider.defaults.xsrfCookieName = 'csrftoken';
    $httpProvider.defaults.xsrfHeaderName = 'X-CSRFToken';
})
.filter('bytes', function () {
    return function (bytes, precision) {
        units = ['·‡ÈÚ', 'Í¡', 'Ã¡', '√¡', '“¡', 'œ¡'];
        if (bytes === 0) return 0 + ' ' + units[0];
        if (isNaN(parseFloat(bytes)) || !isFinite(bytes)) return '-';
        if (typeof precision === 'undefined') precision = 1;
        var units;
        var number = Math.floor(Math.log(bytes) / Math.log(1000));
        return (bytes / Math.pow(1000, Math.floor(number))).toFixed(precision) + ' ' + units[number];
    }
})
.controller('translationCtrl', function($scope, $rootScope, $http) {
    $scope.limit = 100*1024*1024;
    $scope.error = '';
    $scope.article = null;
    $scope.result = {};

    $scope.isLoad = function () {
        return $scope.article === null;
    } ;

    $scope.translate = function() {
        var fd = new FormData();
        fd.append('article', $scope.article);
        $http({
            method : 'POST',
            url: '/essay/',
            data: fd,
            headers: {'Content-Type': undefined}
        })
        .success(function(data) {
            $scope.result = data;
        })
        .error(function(data) {
            console.log('Error: ' + data);
        });

    };

});

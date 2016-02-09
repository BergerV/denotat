'use strict';

angular.module('denotatApp', [
    'ui.bootstrap',                 // Ui Bootstrap
    'bootstrap.fileField'
])
.config(function ($httpProvider) {
    $httpProvider.defaults.xsrfCookieName = 'csrftoken';
    $httpProvider.defaults.xsrfHeaderName = 'X-CSRFToken';
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

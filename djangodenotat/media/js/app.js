'use strict';

angular.module('denotatApp', [
    'ui.bootstrap',                 // Ui Bootstrap
    'bootstrap.fileField'
])

.controller('translationCtrl', function($scope, $rootScope, $http) {
    $scope.limit = 100*1024*1024;
    $scope.error = '';
    $scope.article = null;

    $scope.isLoad = function () {
        return $scope.article === null;
    } ;

    $scope.translate = function() {
        var fd = new FormData();
        fd.append('test', $scope.article);
        $http({
            method : 'POST',
            url: '/essay',
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

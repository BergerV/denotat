/* @preserve
 *
 * angular-bootstrap-file
 * https://github.com/itslenny/angular-bootstrap-file-field
 *
 * Version: 0.1.3 - 02/21/2015
 * License: MIT
 */

angular.module('bootstrap.fileField',[])
.directive('fileField', function($q) {
  var slice = Array.prototype.slice;
  return {
    require:'ngModel',
      scope: {
        limit: '=limit',
        error: '=error'
      },
    restrict: 'E',
    link: function (scope, element, attrs, ngModel) {
        //set default bootstrap class
        if(!attrs.class && !attrs.ngClass){
            element.addClass('btn');
        }

        function filesSizeLimit(files, limit) {
            limit = limit || 2*1024*1024;
            var sum = 0;
            angular.forEach(files, function(file) {
                sum += file.size;
            });
            return sum > limit;
        }

        var fileField = element.find('input');

        fileField.bind('change', function(e) {
            var element = e.target;

            $q.all(slice.call(element.files, 0).map(readFile))
                .then(function(values) {
                    if (element.multiple) {
                        var res = filesSizeLimit(values, scope.limit) ? [] : values;
                        ngModel.$setViewValue(res);
                        scope.error = res.length === 0;
                    }
                    else ngModel.$setViewValue(values.length ? values[0] : null);
                });

            function readFile(file) {
                var deferred = $q.defer();
                deferred.resolve(file);
                /*var reader = new FileReader();
                reader.onload = function(e) {
                    deferred.resolve(e.target.result);
                };
                reader.onerror = function(e) {
                    deferred.reject(e);
                };
                reader.readAsDataURL(file);
                */
                return deferred.promise;
            }

        }); //change

        fileField.bind('click',function(e){
            e.stopPropagation();
        });
        element.bind('click',function(e){
            e.preventDefault();
            fileField[0].click()
        });        
    },
    template:'<button type="button"><ng-transclude></ng-transclude><input type="file" style="display:none"></button>',
    replace:true,
    transclude:true
  };
});
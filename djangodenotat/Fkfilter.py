from django.contrib.admin.filterspecs import RelatedFilterSpec, FilterSpec
from django.utils.translation import ugettext as _
from django.utils.encoding import smart_unicode
class FKFilterSpec(RelatedFilterSpec):
    """
    This code allows you to add a filter on a property of a foreign
    key related model to your model's Django Admin changelist. E.g. if
    you have a model called Book, with a field "type", and you have
    another model called Author, with a FK field "book" to Book, then
    you can add a filter on the Author changelist, by book type.

    Put the code in a file and import it in urls.py, so the filter is
    registered.

    In your app's admin.py, define your model's ModelAdmin class, and
    specify the field in the related model you want to filter.

    For example, using the Book and Author models, you need to define

    class AuthorAdmin(admin.ModelAdmin):
        ....
        book_fk_filter_by = 'type'
        book_fk_filter_name = 'type'
        ...
        list_filter = (..., 'book', ...)
        ...
    
    The <fieldname>_fk_filter_by attribute in ModelAdmin specifies the
    related model property that you want to filter on. The
    <fieldname>_fk_filter_name attribute specifies what is shown on

    the filter sidebar.

    You can also follow more than one relationship. E.g.:

        book_fk_filter_by = 'type__id'
        book_fk_filter_display_field = 'type__type'
        book_fk_filter_name = 'type'

    Here I am assuming from Book model, there is a field 'type' that's
    a FK to a Type model, and the Type model has a field 'id' and a
    field 'type'.

    <fieldname>_fk_filter_display_field specifies which field contains
    values that you want to show on the filter list. For example, as
    shown above, it is a good practice to filter by Type.id in the URL
    and SQL query, but list Type.type in the UI.

    Note that you don't have to change the model to specify the filter
    using a field property. I always find it weird that for something
    that's Django Admin specific, you have to include a line in the
    model to specify the filter.

    FKFilterSpec subclasses from RelatedFilterSpec, and in fact
    replaces RelatedFilterSpec (it's registered ahead of
    RelatedFilterSpec). If you just want to have the default filter by
    a foreign key field (which filters by FK object, not by a property
    on the FK related model), FKFilterSpec still provides that
    behavior.

    When filtering by foreign key field, FKFilterSpec can also limit
    the filtering options (i.e. what is listed in the filter UI) to

    only those FK objects that are related to your model. This works
    for all FK relationships, but not generic relationships from
    Django ContentType package.

    For example, if you have an Author model with a FK to Institution
    model, you can configure Author's changelist to include a filter
    on Institution, but only allow you to select institutions that
    have authors. Institutions that do not have authors won't show up
    on the list.

    To enable this, in your model's ModelAdmin class, set

        <fieldname>_fk_filter_related_only=True
        <fieldname>_fk_filter_display_field=<display this field of the related m
odel in filter list>

    For example, in your AuthorAdmin class, you can do

        institution_fk_filter_related_only=True
        institution_fk_filter_display_field='name'

    You can also further limit the filters, based on certain
    criterias. E.g.:

        def more_filter(self,queryset):
            return queryset.filter(institution__country="US")
        institution_fk_filter_criteria_fn=more_filter

    Note that if _fk_filter_related_only is NOT set to True OR if the
    relationship is a generic relationship from Django ContentType,
    then the function filters a queryset on the model of the FK field.

    Otherwise, if _fk_filter_related_only is True, then the function
    filters a queryset on your model, not the model of the FK field.
    So how define the filter function depends on the
    _fk_filter_related_only setting.

    If you use _fk_filter_criteria_fn, you mostly likely will want to
    augment the query string used in the URLs in the filters, so that
    when you click on a filter option, the correct criteria are all
    present. By default, Django Admin only adds the _pk criteria. For
    example, using the Author and Book models, you can define the
    following in AuthorAdmin:

        book_fk_filter_by = 'type__id'
        book_fk_filter_display_field = 'type__type'
        book_fk_filter_name = 'type'
        def filter_published(self,queryset):
            return queryset.filter(book__published=1)
        book_fk_filter_criteria_fn=filter_published
        book_fk_filter_query_string={ 'book__published' : 1 }

    If you don't specify the _fk_filter_query_string option, then when
    user clicks on a book type, say "Science Fiction", they will see
    all authors of that category, including those authors from
    unpublished books, even though you can limited the types to only
    types of published books.


    """

    def __init__(self, f, request, params, model, model_admin):
        filter_by_key = f.name+'_fk_filter_by'
        filter_by_val = getattr(model_admin, filter_by_key, None)
            
        filter_related_key = f.name+'_fk_filter_related_only'
        filter_related_val = getattr(model_admin, filter_related_key, False)

        filter_nf_key = f.name+'_fk_filter_display_field'
        if filter_by_val != None:
            filter_nf_val = getattr(model_admin, filter_nf_key, filter_by_val)
        else:
            filter_nf_val = getattr(model_admin, filter_nf_key, 'pk')

        filter_crit_key = f.name+'_fk_filter_criteria_fn'
        filter_crit_fn = getattr(model_admin, filter_crit_key, None)

        filter_qs_key = f.name+'_fk_filter_query_string'
        self.filter_qs_val = getattr(model_admin, filter_qs_key, {})

        if filter_by_val != None:
            self.fk_filter_on = True
            # we call FilterSpec constructor, not RelatedFilterSpec
            # constructor; RelatedFilterSpec constructor will try to
            # get all the pk values on the related models, which we
            # won't need.
            FilterSpec.__init__(self, f, request, params, model, model_admin)

            filter_name_key = f.name+'_fk_filter_name'
            filter_name_val = getattr(model_admin, filter_name_key, None)

            if filter_name_val == None:

                self.lookup_title = f.verbose_name
            else:
                self.lookup_title = f.verbose_name+' '+filter_name_val

            self.lookup_kwarg = f.name+'__'+filter_by_val+'__exact'
            self.lookup_val = request.GET.get(self.lookup_kwarg, None)

            if filter_related_val:
                try:
                    qs = model_admin.queryset(request)
                    if filter_crit_fn != None:
                        qs = filter_crit_fn(qs)
                    qs = qs.values_list(f.name+'__'+filter_by_val,f.name+'__'+filter_nf_val).order_by(f.name+'__'+filter_nf_val).distinct()
                except Exception as e:
                    # Django QuerySet can't follow generic
                    # relationships using __, so we have to use
                    # f.rel.to.objects
                    qs = f.rel.to.objects
                    if filter_crit_fn != None:
                        qs = filter_crit_fn(qs)
                    qs = qs.values_list(filter_by_val, filter_nf_val).distinct()
            else:
                qs = f.rel.to.objects
                if filter_crit_fn != None:
                    qs = filter_crit_fn(qs)
                qs = qs.values_list(filter_by_val, filter_nf_val).distinct()

            self.lookup_choices = list(qs)
            # if there was a further limiting criteria, then we want
            # to make sure we still display the filter even if there

            # is only one option
            if filter_crit_fn != None and len(self.lookup_choices) == 1:
                self.lookup_choices = self.lookup_choices+[('',''),]

        else:
            self.fk_filter_on = False
            RelatedFilterSpec.__init__(self, f, request, params, model, model_admin)

            if filter_related_val:
                qs = model_admin.queryset(request)
                if filter_crit_fn != None:
                    qs = filter_crit_fn(qs)
                qs = qs.values_list(f.name+'__pk',f.name+'__'+filter_nf_val).order_by(f.name+'__'+filter_nf_val).distinct()
                self.lookup_choices = list(qs)

    def choices(self, cl):
        qs_all = self.filter_qs_val.keys()
        qs_all.append(self.lookup_kwarg)
        yield {'selected': self.lookup_val is None,
               'query_string': cl.get_query_string({}, qs_all),
               'display': _('All')}
        for pk_val,val in self.lookup_choices:
            qs = self.filter_qs_val
            qs[self.lookup_kwarg] = pk_val
            yield {'selected': self.lookup_val == smart_unicode(pk_val),
                   'query_string': cl.get_query_string(qs),
                   'display': val}

FilterSpec.filter_specs.insert(0, (lambda f: bool(f.rel), FKFilterSpec))

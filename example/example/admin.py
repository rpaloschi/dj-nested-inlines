from django.contrib import admin
from nested_inlines.admin import NestedModelAdmin, NestedTabularInline, NestedStackedInline

from models import A, B, C

class CInline(NestedTabularInline):
    model = C
    exclude = ('owner',)


class BInline(NestedStackedInline):
    model = B
    exclude = ('owner',)
    inlines = [CInline,]


class AAdmin(NestedModelAdmin):
    exclude = ('owner',)
    inlines = [BInline,]

    def save_model(self, request, obj, form, change):
        obj.owner_id = request.user.id

        super(AAdmin, self).save_model(request, obj, form, change)


    def save_formset(self, request, form, formset, change):
        """
        Given an inline formset save it to the database.
        """
        print "save_formset override (A)"

        instances = formset.save(commit=False)
        for instance in instances:
            print "instance: ", instance

            instance.owner_id = request.user.id
            instance.save()

        formset.save()
        # this save_m2m arrives from an official django example:
        # https://docs.djangoproject.com/en/1.5/ref/contrib/admin/#django.contrib.admin.ModelAdmin.save_formset
        # and is different from the save_formset defined in django_nested_inlines extension
        # formset.save_m2m()

        #iterate through the nested formsets and save them
        #skip formsets, where the parent is marked for deletion
        if formset.can_delete:
            deleted_forms = formset.deleted_forms
        else:
            deleted_forms = []
        for form in formset.forms:
            if hasattr(form, 'nested_formsets') and form not in deleted_forms:
                for nested_formset in form.nested_formsets:
                    self.save_formset(request, form, nested_formset, change)


admin.site.register(A, AAdmin)

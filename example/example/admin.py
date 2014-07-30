from django.contrib import admin
from django.core.exceptions import ValidationError
from nested_inlines.admin import NestedModelAdmin, NestedTabularInline, NestedStackedInline

from models import A, B, C

class OwnerException(Exception):
    pass

class CInline(NestedTabularInline):
    model = C
    exclude = ('id', 'owner')
    max_num = 1
    extra = 0

    def get_readonly_fields(self, request, obj=None):
        # import pdb ; pdb.set_trace()
        fieldnames = [x.name for x in self.model._meta.fields]
        print "GET_READONLY_FIELDS C: ", obj

        if hasattr(self, "exclude") and self.exclude is not None:
            return tuple( set(fieldnames) - set(self.exclude) )
        else:
            return tuple(fieldnames)

class BInline(NestedStackedInline):
    model = B
    exclude = ('id', 'owner')
    inlines = [CInline,]
    max_num = 1
    extra = 0

    def get_readonly_fields(self, request, obj=None):
        fieldnames = [x.name for x in self.model._meta.fields]
        # import pdb ; pdb.set_trace()
        print "GET_READONLY_FIELDS B: ", obj

        if hasattr(self, "exclude") and self.exclude is not None:
            return tuple( set(fieldnames) - set(self.exclude) )
        else:
            return tuple(fieldnames)

class AAdmin(NestedModelAdmin):
    exclude = ('id', 'owner')
    inlines = [BInline,]
    max_num = 1
    extra = 0

    def save_model_off(self, request, obj, form, change):        
        print "save_model override (A) change: ", ("TRUE" if change else "FALSE")
        if change:
            print "OWNED: ", ("YES" if obj.is_owned_by(request.user, include_superuser=True) else "NO")
            if not obj.is_owned_by(request.user, include_superuser=True):
                raise ValidationError("ototo")

        if not change:
            obj.owner_id = request.user.id
        else:
            if not obj.owner_id:
                raise OwnerException("Inconsistent record %d, no owner id found" % request.pk)

        # ugly but works
        request._gem_custom = obj.owner_id
        super(AAdmin, self).save_model(request, obj, form, change)


    def save_formset_off(self, request, form, formset, change):
        """
        Given an inline formset save it to the database.
        """
        print "save_formset override (A) ", request._gem_custom

        instances = formset.save(commit=False)
        for instance in instances:
            print "instance: ", instance
            # import pdb ; pdb.set_trace()
            
            if hasattr(instance, "owner_id"):
                instance.owner_id = request._gem_custom
            instance.save()
        # formset.save()
        formset.save_m2m()

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

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def get_readonly_fields(self, request, obj=None):
        # import pdb ; pdb.set_trace()
        fieldnames = [x.name for x in self.model._meta.fields]
        print "GET_READONLY_FIELDS A: ", obj

        if hasattr(self, "exclude") and self.exclude is not None:
            return tuple( set(fieldnames) - set(self.exclude) )
        else:
            return tuple(fieldnames)

admin.site.register(A, AAdmin)

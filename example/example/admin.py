from django.contrib import admin
from django.core.exceptions import ValidationError
from nested_inlines.admin import NestedModelAdmin, NestedTabularInline, NestedStackedInline

from models import A, B, C

# import pdb

class OwnerException(Exception):
    pass

class MissingOwnerException(Exception):
    pass


class OwnedNestedStackedInline(NestedStackedInline):
    def get_readonly_fields(self, request, obj=None):
        if request.user.is_superuser:
            return ()

        if not hasattr(request, '_gem_owner_id') or not request._gem_owner_id:
            raise MissingOwnerException('OwnedNestedStackedInline missing owner')

        fieldnames = tuple([x.name for x in self.model._meta.fields])

        if "owner" in fieldnames and "owner" not in self.exclude:
            plus_owner = ("owner",)
        else:
            plus_owner = ()

        if request._gem_owner_id == request.user.id:
            # print "PRINTTTTOWN: ", plus_owner
            return tuple(plus_owner)
        # pdb.set_trace()
        # print "GET_READONLY_FIELDS B: ", obj

        self.can_delete = False

        if hasattr(self, "exclude") and self.exclude is not None:
            return tuple( set(fieldnames + plus_owner) - set(self.exclude) )
        else:
            return tuple(set(fieldnames + plus_owner))

    def has_add_permission(self, request):
        if request.user.is_superuser:
            self.exclude = ('id',)
        return super(OwnedNestedStackedInline, self).has_add_permission(request)


class CInline(OwnedNestedStackedInline):
    model = C
    exclude = ('id', 'owner')
    max_num = 1
    extra = 1


    def __getattribute__off(self, name):
        cc = object.__getattribute__(self, name)
        if callable(cc):
            print "CInline call:   %s" % name
        else:
            print "CInline access: %s" % name
        return cc


class BInline(OwnedNestedStackedInline):
    model = B
    exclude = ('id', 'owner')
    inlines = [CInline,]
    max_num = 1
    extra = 1


class AAdmin(NestedModelAdmin):
    exclude = ('id',)
    inlines = [BInline,]
    max_num = 1
    extra = 0

    def save_model(self, request, obj, form, change):
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


    def has_add_permission(self, request):
        if request.user.is_superuser:
            self.exclude = ('id',)
        return super(AAdmin, self).has_add_permission(request)

    def has_delete_permission(self, request, obj=None):
        if not obj or obj.is_owned_by(request.user, include_superuser=True):
            return True
        else:
            return False


    def get_readonly_fields(self, request, obj=None):
        # pdb.set_trace()
        if request.user.is_superuser:
            return ()

        if obj:
            if hasattr(obj, "owner"):
                request._gem_owner_id = obj.owner.id
            else:
                request._gem_owner_id = None
        else:
            request._gem_owner_id = request.user.id

        # if superuser:
        #     return ()

        # OLD OK fieldnames = tuple([x.name for x in self.model._meta.fields])
        fieldnames = tuple( set([x.name for x in self.model._meta.fields]) - set(self.exclude))
        # print "FNA", fieldnames
        if "owner" in fieldnames and "owner" not in self.exclude:
            plus_owner = ("owner",)
        else:
            plus_owner = ()

        if obj is None or obj.owner.id == request.user.id:
            # print "PRINTTTTOWN: ", plus_owner
            return tuple(plus_owner)

        self.can_delete = False

        # pdb.set_trace()
        # print "GET_READONLY_FIELDS A: ", obj

        if hasattr(self, "exclude") and self.exclude is not None:
            return tuple( set(fieldnames + plus_owner) - set(self.exclude) )
        else:
            return tuple(set(fieldnames + plus_owner))

    def save_formset(self, request, form, formset, change):
        """
        Given an inline formset save it to the database.
        """
        print "save_formset override (A) ", request._gem_custom

        instances = formset.save(commit=False)
        for instance in instances:
            # cascading ownership from first ancestor just for normal users
            if not request.user.is_superuser:
                if hasattr(instance, "owner_id"):
                    instance.owner_id = request._gem_custom
            instance.save()
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



admin.site.register(A, AAdmin)

from django.contrib import admin
from nested_inlines.admin import NestedModelAdmin, NestedTabularInline, NestedStackedInline

from models import A, B, C

class CInline(NestedTabularInline):
    model = C
    exclude = ('owner',)

    def save_model_off(self, request, obj, form, change):
        # save C
        import pdb ; pdb.set_trace()
        obj.owner_id = request.user.id
        obj.save()


class BInline(NestedStackedInline):
    model = B
    exclude = ('owner',)
    inlines = [CInline,]

    def formfield_for_foreignkey_off(self, db_field, request, **kwargs):
        # if db_field.name == "car":
        #     kwargs["queryset"] = Car.objects.filter(owner=request.user)
        import pdb ; pdb.set_trace()
        return super(MyModelAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)

    def save_model_off(self, request, obj, form, change):
        # save B
        import pdb ; pdb.set_trace()
        obj.owner_id = request.user.id
        obj.save()


    def save_formset_off_orig(self, request, form, formset, change):
        # save_formset BAdmin
        import pdb ; pdb.set_trace()
        instances = formset.save(commit=False)
        for instance in instances:
            instance.owner_id = request.user.id
            instance.save()
        formset.save_m2m()

    def save_formset(self, request, form, formset, change):
        """
        Given an inline formset save it to the database.
        """
        print "save_formset override (B)"
        import pdb ; pdb.set_trace()

        formset.save()
        
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

    
class AAdmin(NestedModelAdmin):
    exclude = ('owner',)
    inlines = [BInline,]

    def save_model_ok01(self, request, obj, form, change):
        # save A
        # import pdb ; pdb.set_trace()
        obj.owner_id = request.user.id
        
        obj.save()

    def save_model(self, request, obj, form, change):
        # save A
        # import pdb ; pdb.set_trace()
        obj.owner_id = request.user.id
        
        super(AAdmin, self).save_model(request, obj, form, change)


    def save_formset_off_orig(self, request, form, formset, change):
        # save_formset AAdmin
        import pdb ; pdb.set_trace()
        instances = formset.save(commit=False)
        for instance in instances:
            instance.owner_id = request.user.id
            instance.save()
        formset.save_m2m()
    
    def save_formset(self, request, form, formset, change):
        """
        Given an inline formset save it to the database.
        """
        print "save_formset override (A)"
        # import pdb ; pdb.set_trace()


        instances = formset.save(commit=False)
        for instance in instances:
            print "HELLO: ", instance
            # import pdb ; pdb.set_trace()
            
            instance.owner_id = request.user.id
            instance.save()

        formset.save()
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

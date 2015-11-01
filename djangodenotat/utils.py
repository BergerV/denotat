def get_or_none(model, **kwargs):
    try:
        return model.objects.get(**kwargs)
    except model.DoesNotExist:
        return None
    
def flatten(x):
    flat = True
    ans = []
    for i in x:
        if ( i.__class__ is list):
            ans = flatten(i)
        else:
            ans.append(i)
    return ans    

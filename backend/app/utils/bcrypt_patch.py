import bcrypt

# If bcrypt was built natively but __about__ metadata is missing,
# inject a minimal stub so Passlib stops warning.
if not hasattr(bcrypt, "__about__"):
    import types
    about = types.SimpleNamespace(__version__=getattr(bcrypt, "__version__", "4.1.3"))
    bcrypt.__about__ = about

site_domain = os.environ.get('SITE_DOMAIN', 'connectbracuacbd.vercel.app')
site, _ = Site.objects.get_or_create(pk=1, defaults={'domain': site_domain, 'name': 'BRAC University'})
if site.domain != site_domain:
    site.domain = site_domain
    site.save()
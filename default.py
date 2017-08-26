# -*- coding: cp1252 -*-

""" -*- coding: utf-8 -*- """
#
# version 0.0.1 - By SlySen
#
# pylint...: --max-line-length 120
# vim......: set expandtab
# vim......: set tabstop=4
#
import os, time, urllib, urllib2, re, socket, sys, traceback, xbmcplugin, xbmcaddon, xbmcgui, xbmc, simplejson
# import SimpleDownloader, unicodedata
if sys.version >= "2.5":
    from hashlib import md5 as _hash
else:
    from md5 import new as _hash


ADDON = xbmcaddon.Addon()
ADDON_CACHE_BASEDIR = os.path.join(xbmc.translatePath(ADDON.getAddonInfo('path')), ".cache")
ADDON_CACHE_TTL = float(ADDON.getSetting('CacheTTL').replace("0", ".5").replace("73", "0"))
ADDON_ICON = ADDON.getAddonInfo('icon')
ADDON_NAME = ADDON.getAddonInfo('name')
ADDON_IMAGES_BASEPATH = ADDON.getAddonInfo('path')+'/resources/media/images/'
ADDON_FANART = ADDON.getAddonInfo('path')+'/fanart.jpg'
RE_HTML_TAGS = re.compile(r'<[^>]+>')
RE_AFTER_CR = re.compile(r'\n.*')

#DOWNLOAD_FOLDER = str(ADDON.getSetting('download_folder'))
#DOWNLOAD_QUALITY = int(ADDON.getSetting('download_quality'))

TV5CA_VIDEO_SITE = 'unis.ca'
TV5CA_BASE_URL = 'http://'+TV5CA_VIDEO_SITE

if not os.path.exists(ADDON_CACHE_BASEDIR):
    os.makedirs(ADDON_CACHE_BASEDIR)

def is_cached_content_expired(last_update):
    """ function docstring """
    expired = time.time() >= (last_update + (ADDON_CACHE_TTL * 60**2))
    return expired

def get_cached_filename(path):
    """ function docstring """
    filename = "%s" % _hash(repr(path)).hexdigest()
    return os.path.join(ADDON_CACHE_BASEDIR, filename)

def get_cached_content(path):
    """ function docstring """
    content = None
    try:
        filename = get_cached_filename(path)
        if os.path.exists(filename) and not is_cached_content_expired(os.path.getmtime(filename)):
            content = open(filename).read()
        else:
            content = get_url_txt(path)
            try:
                file(filename, "w").write(content) # cache the requested web content
            except StandardError:
                traceback.print_exc()
    except StandardError:
        return None
    return content

# Merci à l'auteur de cette fonction
def unescape_callback(matches):
    """ function docstring """
    html_entities =\
    {
        'quot':'\"', 'amp':'&', 'apos':'\'', 'lt':'<',
        'gt':'>', 'nbsp':' ', 'copy':'©', 'reg':'®',
        'Agrave':'À', 'Aacute':'Á', 'Acirc':'Â',
        'Atilde':'Ã', 'Auml':'Ä', 'Aring':'Å',
        'AElig':'Æ', 'Ccedil':'Ç', 'Egrave':'È',
        'Eacute':'É', 'Ecirc':'Ê', 'Euml':'Ë',
        'Igrave':'Ì', 'Iacute':'Í', 'Icirc':'Î',
        'Iuml':'Ï', 'ETH':'Ð', 'Ntilde':'Ñ',
        'Ograve':'Ò', 'Oacute':'Ó', 'Ocirc':'Ô',
        'Otilde':'Õ', 'Ouml':'Ö', 'Oslash':'Ø',
        'Ugrave':'Ù', 'Uacute':'Ú', 'Ucirc':'Û',
        'Uuml':'Ü', 'Yacute':'Ý', 'agrave':'à',
        'aacute':'á', 'acirc':'â', 'atilde':'ã',
        'auml':'ä', 'aring':'å', 'aelig':'æ',
        'ccedil':'ç', 'egrave':'è', 'eacute':'é',
        'ecirc':'ê', 'euml':'ë', 'igrave':'ì',
        'iacute':'í', 'icirc':'î', 'iuml':'ï',
        'eth':'ð', 'ntilde':'ñ', 'ograve':'ò',
        'oacute':'ó', 'ocirc':'ô', 'otilde':'õ',
        'ouml':'ö', 'oslash':'ø', 'ugrave':'ù',
        'uacute':'ú', 'ucirc':'û', 'uuml':'ü',
        'yacute':'ý', 'yuml':'ÿ'
    }

    entity = matches.group(0)
    val = matches.group(1)

    try:
        if entity[:2] == r'\u':
            return entity.decode('unicode-escape')
        elif entity[:3] == '&#x':
            return unichr(int(val, 16))
        elif entity[:2] == '&#':
            return unichr(int(val))
        else:
            return html_entities[val].decode('utf-8')

    except (ValueError, KeyError):
        pass

def html_unescape(data):
    """ function docstring """
    data = data.decode('utf-8')
    data = re.sub(r'&#?x?(\w+);|\\\\u\d{4}', unescape_callback, data)
    data = data.encode('utf-8')
    return data

def rechercher_un_element(argument, rechercher_dans):
    """ function docstring """
    reponse = re.compile(argument, re.DOTALL).search(rechercher_dans)
    if reponse:
        return reponse.group(1)
    else:
        return ""

def get_url_txt(the_url):
    """ function docstring """
    check_for_internet_connection()
    req = urllib2.Request(the_url)
    req.add_header(\
        'User-Agent',\
        'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:19.0) Gecko/20100101 Firefox/19.0'\
    )
    req.add_header('Accept-Charset', 'utf-8')
    response = urllib2.urlopen(req)
    link = response.read()
    link = html_unescape(link)
    response.close()
    return link

def creer_menu_accueil():
    """ function docstring """

    add_dir('A %C3%A0 Z - Toutes les vid%C3%A9os',\
            TV5CA_BASE_URL+'/videos?options[sort]=title&options[order]=ASC&options[page]=1', \
            6, ADDON_IMAGES_BASEPATH+'default-folder.png', True\
    )
    add_dir('Cat%C3%A9gories',\
            TV5CA_BASE_URL+'/videos',\
            7, ADDON_IMAGES_BASEPATH+'default-folder.png', True\
    )
    add_dir('Titres',\
            TV5CA_BASE_URL+'/videos',\
            8, ADDON_IMAGES_BASEPATH+'default-folder.png', True\
    )
    add_dir('-- %C3%80 voir',\
            TV5CA_BASE_URL,\
            5, ADDON_IMAGES_BASEPATH+'default-folder.png', True\
    )
    add_dir('-- Populaires',\
            TV5CA_BASE_URL+'/videos?options[sort]=meta.hits&options[order]=DESC&options[page]=1',\
            6, ADDON_IMAGES_BASEPATH+'default-folder.png', True\
    )
    add_dir('-- R%C3%A9cents',\
            TV5CA_BASE_URL+'/videos?options[sort]=publish_start&options[order]=DESC&options[page]=1',\
            6, ADDON_IMAGES_BASEPATH+'default-folder.png', True\
    )
    add_dir('[COLOR ffabb904][I]Param%C3%A8tres de l\'additiciel...[/I][/COLOR]',\
            TV5CA_BASE_URL,\
            99, ADDON_IMAGES_BASEPATH+'default-folder.png', False\
    )

def creer_menu_categories(the_url):
    """ function docstring """
    link = get_cached_content(the_url)
    container = re.split('<div class="selectlist-video-filters js-selectlist-video-filters">', link)
    liste = re.split('<option', container[2])
    for item in liste:
        theme = rechercher_un_element('value="(.+?)"', item)
        if theme is not '':
            theme_title = rechercher_un_element('>(.+?)</option>', item)
            add_dir(\
                theme_title,\
                TV5CA_BASE_URL+\
                    '/videos?options[sort]=title&options[order]=ASC&params[theme]='+theme+'&options[page]=1',\
                6, ADDON_IMAGES_BASEPATH+'default-folder.png', True\
            )

def creer_menu_titres(the_url):
    """ function docstring """
    link = get_cached_content(the_url)
    container = re.split('<div class="selectlist-video-filters js-selectlist-video-filters">', link)
    liste = re.split('<option', container[1])
    for item in liste:
        serie = rechercher_un_element('value="(.+?)"', item)
        if serie is not '':
            serie_title = rechercher_un_element('>(.+?)</option>', item)
            add_dir(\
                serie_title,\
                TV5CA_BASE_URL+\
                    '/videos?options[sort]=title&options[order]=ASC&params[serie]='+serie+'&options[page]=1',\
                6, ADDON_IMAGES_BASEPATH+'default-folder.png', True\
            )

def creer_liste_videos_orphelines(the_url, the_carousel_class_name):
    """ function docstring """
    link = get_cached_content(the_url)
    currentpage = rechercher_un_element(r'options\[page\]=(\d+)', the_url)

    container = re.split('<div class="'+the_carousel_class_name+'"', link)
    container = re.split('<div class="pagination-block', container[1])
    liste = re.split('<div class="media-thumb', container[0])
    media_url_list = []
    got_video = False
    for item in liste:
        url_episode = rechercher_un_element('<a href="(.+?)"', item) or None
        if url_episode is not None and len(url_episode) > 5:
            got_video = True
        nom_emission = rechercher_un_element('<h3 class="t2">(.+?)</h3>', item) or\
            rechercher_un_element('<h3 class="t3">(.+?)</h3>', item)
        nom_episode = rechercher_un_element('<p>(.+?)<br />', item) or ""
        icon = rechercher_un_element('data-src="(.+?)"', item)
        duree = get_duration_in_seconds(rechercher_un_element('duration">(.+?)</span>', item))
        rating = rechercher_un_element('data-rating="(.+?)"', item) or ""
        deadline = rechercher_un_element('<strong>(.+?)</strong>', item) or ""

        if nom_episode is not "":
            name = nom_emission+' : '+nom_episode
        else:
            name = nom_emission
        if is_int(rating) == True:
            name = name + ' [' + rating + '+]'

        if url_episode:
            # Pour eviter les duplication (surtout dans Populaires et Recents)
            try:
                log('media_url_list.index:'+str(media_url_list.index(nom_emission+' : '+nom_episode)))
            except ValueError:
                media_url_list.append(nom_emission+' : '+nom_episode)
                add_link(\
                    name,\
                    TV5CA_BASE_URL+url_episode,\
                    icon,\
                    deadline,\
                    duree
                )

    if got_video == False:
        xbmcgui.Dialog().ok(\
            ADDON_NAME,\
            ADDON.getLocalizedString(32120),\
            ADDON.getLocalizedString(32121)\
        )
        exit()
    else:
        try:
            pagecount = get_pagination_pagecount(link)
            nextpage = int(currentpage) + 1
            add_bottom_navigation_items(\
                the_url.replace('options[page]='+currentpage, 'options[page]='+str(nextpage)),\
                MODE, nextpage, pagecount\
            )
        except:
            pass

def get_pagination_pagecount(page_content):
    """ function docstring """
    container = re.split('<div class="pagination mobile ">', page_content)
    pagecount = rechercher_un_element('<span class="last-page js-last-page">(.+?)</span>', container[1])
    return pagecount

def get_duration_in_seconds(duree_block):
    """ function docstring """
    duree = rechercher_un_element(r'(\d+:\d+:\d+)', duree_block)
    if not duree:
        duree = rechercher_un_element(r'(\d+:\d+)', duree_block)
        if not duree:
            duree = -1
        else:
            d_entries = re.findall(r'(\d+):(\d+)', duree)
            duree = int(d_entries[0][0])*60+int(d_entries[0][1])
    else:
        # hh:mm:ss
        d_entries = re.findall(r'(\d+):(\d+):(\d+)', duree)
        duree = int(d_entries[0][0])*60*60+int(d_entries[0][1])*60+int(d_entries[0][2])

    if not duree:
        return -1
    elif duree < 60:
        return -1
    else:
        return duree

def jouer_video(the_url):
    """ function docstring
        PlaylistService:
            http://production.ps.delve.cust.lldns.net/r/PlaylistService/media/f727ceb744a9414f94409faf6b3fddbb/getPlaylistByMediaId
    """
    check_for_internet_connection()
    link = get_cached_content(the_url)

    # Obtenir media_uid pure de l'émission
    media_uid = rechercher_un_element('"mediaId":"(.+?)"', link)

    # Obtenir JSON avec liens RTMP du playlistService
    video_json = simplejson.loads(\
        get_cached_content(\
            'http://production.ps.delve.cust.lldns.net/r/PlaylistService/media/%s/getPlaylistByMediaId' % media_uid\
        )\
    )

    # Preparer list de videos à jouer
    playlist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
    playlist.clear()

    # Analyser chaque stream disponible pour trouver la meilleure qualité
    for play_list_item in video_json['playlistItems']:
        highest_bit_rate = 0
        stream_url = None
        for stream in play_list_item['streams']:
            if stream['videoBitRate'] > highest_bit_rate:
                highest_bit_rate = stream['videoBitRate']
                stream_url = stream['url']

        if stream_url:
            # Générer un lien compatible pour librtmp
            # rtmp_url - play_path - swf_url
            url_final = '%s playPath=%s swfUrl=%s swfVfy=true' % (\
                stream_url[:stream_url.find('mp4')],\
                stream_url[stream_url.find('mp4'):],\
                'http://s.delvenetworks.com/deployments/flash-player/flash-player-5.10.1.swf?playerForm=Chromeless'\
            )

            log('Starting playback of :' + urllib.quote_plus(url_final))
            item = xbmcgui.ListItem(\
                video_json['title'],\
                iconImage=video_json['imageUrl'],\
                thumbnailImage=video_json['imageUrl']\
            )
            playlist.add(url_final, item)
        else:
            xbmc.executebuiltin('Notification(%s,Incapable d''obtenir lien du video,5000,%s' % (ADDON_NAME, ADDON_ICON))

    if playlist.size() > 0:
        player = None
        try:
            player = xbmc.Player(xbmc.PLAYER_CORE_DVDPLAYER)
        except Exception:
            player = xbmc.Player()
            pass

        player.play(playlist)

def get_params():
    """ function docstring """
    param = []
    paramstring = sys.argv[2]
    if len(paramstring) >= 2:
        params = sys.argv[2]
        cleanedparams = params.replace('?', '')
        if params[len(params)-1] == '/':
            params = params[0:len(params)-2]
        pairsofparams = cleanedparams.split('&')
        param = {}
        for i in range(len(pairsofparams)):
            splitparams = {}
            splitparams = pairsofparams[i].split('=')
            if (len(splitparams)) == 2:
                param[splitparams[0]] = splitparams[1]

    return param

def add_bottom_navigation_items(url, mode, nextpage, pagecount):
    """ function docstring """

    # Next Page
    if int(nextpage) <= int(pagecount):
        entry_url = sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)
        liz = xbmcgui.ListItem(\
            '('+ADDON.getLocalizedString(32118)+ ' ' +str(nextpage - 1)+' '+\
            ADDON.getLocalizedString(32119)+' '+str(pagecount)+') '+\
            ADDON.getLocalizedString(32116)\
        )

        if ADDON.getSetting('FanartEnabled') == 'true':
            liz.setProperty('fanart_image', ADDON_FANART)

        xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=entry_url, listitem=liz, isFolder=True)

    # Back to Home page
    if int(nextpage) - 1 is not 1:
        entry_url = sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+'98'
        liz = xbmcgui.ListItem(ADDON.getLocalizedString(32117))
        liz.addContextMenuItems([], replaceItems=True)

        if ADDON.getSetting('FanartEnabled') == 'true':
            liz.setProperty('fanart_image', ADDON_FANART)

        xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=entry_url, listitem=liz, isFolder=True)

    return

def add_dir(name, url, mode, iconimage, is_folder):
    """ function docstring """
    entry_url = sys.argv[0]+"?url="+urllib.quote_plus(url)+\
        "&mode="+str(mode)+\
        "&name="+urllib.quote_plus(name)

    is_it_ok = True
    liz = xbmcgui.ListItem(\
        urllib.unquote(name),\
        iconImage=ADDON_IMAGES_BASEPATH+'default-folder.png',\
        thumbnailImage=iconimage\
    )

    if is_folder is True:
        liz.setInfo(\
            type="Video",\
            infoLabels={\
                "Title": urllib.unquote(name),\
                "plot":\
                    '[B]'+urllib.unquote(name.replace('-- ', ''))+'[/B]'+'[CR]'+\
                    ADDON.getAddonInfo('id')+' v.'+ADDON.getAddonInfo('version')\
            }\
        )

    if ADDON.getSetting('FanartEnabled') == 'true':
        if ADDON.getSetting('FanartEmissionsEnabled') == 'true':
            if iconimage == ADDON_IMAGES_BASEPATH+'default-folder.png': # Main dicrectory listing
                liz.setProperty('fanart_image', ADDON_FANART)
            else:
                liz.setProperty('fanart_image', iconimage)
        else:
            liz.setProperty('fanart_image', ADDON_FANART)
    is_it_ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=entry_url, listitem=liz, isFolder=is_folder)
    return is_it_ok

def add_link(name, the_url, iconimage, plot, duree):
    """ function docstring """
    is_it_ok = True
    entry_url = sys.argv[0]+"?url="+urllib.quote_plus(the_url)+\
        "&mode=4"+\
        "&name="+urllib.quote_plus(name)

    if plot != '':
        if ADDON.getSetting('EmissionNameInPlotEnabled') == 'true':
            plot = '[B]'+plot.lstrip()+'[/B]'+'[CR]'+name.lstrip()
        else:
            plot = name.lstrip()
    else:
        plot = name.lstrip()

    liz = xbmcgui.ListItem(\
        remove_any_html_tags(name),\
        iconImage=ADDON_IMAGES_BASEPATH+"default-video.png",\
        thumbnailImage=iconimage\
    )
    liz.setInfo(\
        type="Video",\
        infoLabels={\
            "Title":remove_any_html_tags(name),\
            "Plot":remove_any_html_tags(plot, False),\
            "Duration":duree\
        }\
    )
    
    # Download Video
    #liz.addContextMenuItems(
    #    [\
    #        ('Informations', 'Action(Info)'),\
    #        (\
    #            ADDON.getLocalizedString(32133),\
    #            'RunPlugin(plugin://'+ADDON.getAddonInfo('id')+'/?mode=50&name='+urllib.quote_plus(name)+'&url='+urllib.quote_plus(the_url)+')'\
    #        ),\
    #    ]\
    #)

    if ADDON.getSetting('FanartEnabled') == 'true':
        if ADDON.getSetting('FanartEmissionsEnabled') == 'true':
            liz.setProperty('fanart_image', iconimage)
        else:
            liz.setProperty('fanart_image', ADDON_FANART)

    is_it_ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=entry_url, listitem=liz, isFolder=False)
    return is_it_ok

def set_content(content):
    """ function docstring """
    xbmcplugin.setContent(int(sys.argv[1]), content)
    return

def set_sorting_methods(mode):
    """ function docstring """
    # c.f.: https://github.com/notspiff/kodi-cmake/blob/master/xbmc/SortFileItem.h
    log('MODE:'+str(mode))
    if mode != None and mode != 1:
        if ADDON.getSetting('SortMethodTvShow') == '1':
            xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_TITLE)
            xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_TITLE_IGNORE_THE)
    return

def is_network_available():
    """ function docstring """
    try:
        # see if we can resolve the host name -- tells us if there is a DNS listening
        host = socket.gethostbyname(TV5CA_VIDEO_SITE)
        # connect to the host -- tells us if the host is actually reachable
        srvcon = socket.create_connection((host, 80), 2)
        srvcon.close()
        return True
    except socket.error:
        return False

def check_for_internet_connection():
    """ function docstring """
    if ADDON.getSetting('NetworkDetection') == 'false':
        return

    if is_network_available() == False:
        xbmcgui.Dialog().ok(\
            ADDON_NAME,\
            ADDON.getLocalizedString(32112),\
            ADDON.getLocalizedString(32113)\
        )
        exit()
    return

def is_int(string):
    """ function docstring """
    try:
        int(string)
        return True
    except ValueError:
        return False

def remove_any_html_tags(text, crlf=True):
    """ function docstring """
    text = RE_HTML_TAGS.sub('', text)
    text = text.lstrip()
    if crlf == True:
        text = RE_AFTER_CR.sub('', text)
    return text

def debug_print(texte):
    """ function docstring """
    entry_url = sys.argv[0]+"?url="+urllib.quote_plus(TV5CA_BASE_URL)+\
        "&mode="+str(0)+\
        "&name="+urllib.quote_plus(texte)
    is_it_ok = True
    liz = xbmcgui.ListItem(texte, iconImage=ADDON_IMAGES_BASEPATH+'default-folder.png', thumbnailImage='')
    liz.setInfo(type="Video", infoLabels={"Title": texte})
    is_it_ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=entry_url, listitem=liz, isFolder=True)
    return is_it_ok

def log(msg):
    """ function docstring """
    if ADDON.getSetting('DebugMode') == 'true':
        xbmc.log('[%s - DEBUG]: %s' % (ADDON_NAME, msg))

# ---
log('--- init -----------------')
# ---

PARAMS = get_params()
URL = None
NAME = None
MODE = None
CURRENTPAGE = 1

try:
    URL = urllib.unquote_plus(PARAMS["url"])
    log("PARAMS['url']:"+URL)
except StandardError:
    pass
try:
    NAME = urllib.unquote_plus(PARAMS["name"])
    log("PARAMS['name']:"+NAME)
except StandardError:
    pass
try:
    MODE = int(PARAMS["mode"])
    log("PARAMS['mode']:"+str(MODE))
except StandardError:
    pass

# Home page
if MODE == None or URL == None or len(URL) < 1:
    creer_menu_accueil()
    set_content('episodes')

# Play video
elif MODE == 4:
    jouer_video(URL)

# A Voir
elif MODE == 5:
    creer_liste_videos_orphelines(URL, 'a-voir-carousel-inner')
    set_content('episodes')

# A-Z Videos, Recents, Populaires
elif MODE == 6:
    creer_liste_videos_orphelines(URL, 'listing-carousel-inner')
    set_content('episodes')

# Filtre par categories
elif MODE == 7:
    creer_menu_categories(URL)
    set_content('episodes')

# Filtre par titres
elif MODE == 8:
    creer_menu_titres(URL)
    set_content('episodes')

# Download
#elif MODE == 50:
#    download_file(URL, NAME)

# Main Menu
elif MODE == 98:
    xbmc.executebuiltin("XBMC.Container.Update(%s, replace)" % (sys.argv[0],))

# Settings
elif MODE == 99:
    ADDON.openSettings()

# Let's get out of here!
if MODE is not 98 or MODE is not 99:
    set_sorting_methods(MODE)
    xbmcplugin.endOfDirectory(int(sys.argv[1]))

if MODE is not 4 and ADDON.getSetting('DeleteTempFiFilesEnabled') == 'true':
    PATH = xbmc.translatePath('special://temp')
    FILENAMES = next(os.walk(PATH))[2]
    for k in FILENAMES:
        if ".fi" in k:
            os.remove(os.path.join(PATH, k))


"""Main application for Discordo TUI client."""

import asyncio
import aiohttp
import logging
import re
import webbrowser
from typing import Optional, List, Tuple, Set
from io import StringIO
from pathlib import Path
from datetime import datetime

from textual.app import ComposeResult, App
from textual.containers import Vertical, Horizontal
from textual.widgets import OptionList, RichLog, Static, ListView, ListItem, Input
from textual.binding import Binding
from textual.message import Message
from rich.panel import Panel
from rich.text import Text

from discordo.internal.config import Config
from discordo.internal.database import DiscordDatabase
from discordo.internal.gateway import DiscordGateway

logger = logging.getLogger(__name__)

# Regex pattern for detecting URLs - uses actual IANA TLD list (1438 TLDs)
# Pattern carefully handles URL characters to avoid truncation
URL_PATTERN = re.compile(
    r'(?:'
    # Match URLs with explicit protocol (http, https, ftp)
    # Allow most URL-safe characters: letters, numbers, -, _, ., ~, :, /, ?, #, [, ], @, !, $, &, ', (, ), *, +, ,, ;, =, %
    r'(?:https?|ftp)://(?:[a-zA-Z0-9\-._~:/?#\[\]@!$&\'()*+,;=%]|(?:%[0-9A-Fa-f]{2}))+'
    r'|'
    # Match www.* links
    r'www\.[a-zA-Z0-9\-]+(?:\.[a-zA-Z]{2,})+(?:[/?#](?:[a-zA-Z0-9\-._~:/?#\[\]@!$&\'()*+,;=%]|(?:%[0-9A-Fa-f]{2}))*)?'
    r'|'
    # Match domain.tld without protocol
    r'(?:[a-zA-Z0-9](?:[a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?\.)+(?:aaa|aarp|abb|abbott|abbvie|abc|able|abogado|abudhabi|ac|academy|accenture|accountant|accountants|aco|actor|ad|ads|adult|ae|aeg|aero|aetna|af|afl|africa|ag|agakhan|agency|ai|aig|airbus|airforce|airtel|akdn|al|alibaba|alipay|allfinanz|allstate|ally|alsace|alstom|am|amazon|americanexpress|americanfamily|amex|amfam|amica|amsterdam|analytics|android|anquan|anz|ao|aol|apartments|app|apple|aq|aquarelle|ar|arab|aramco|archi|army|arpa|art|arte|as|asda|asia|associates|at|athleta|attorney|au|auction|audi|audible|audio|auspost|author|auto|autos|aw|aws|ax|axa|az|azure|ba|baby|baidu|banamex|band|bank|bar|barcelona|barclaycard|barclays|barefoot|bargains|baseball|basketball|bauhaus|bayern|bb|bbc|bbt|bbva|bcg|bcn|bd|be|beats|beauty|beer|berlin|best|bestbuy|bet|bf|bg|bh|bharti|bi|bible|bid|bike|bing|bingo|bio|biz|bj|black|blackfriday|blockbuster|blog|bloomberg|blue|bm|bms|bmw|bn|bnpparibas|bo|boats|boehringer|bofa|bom|bond|boo|book|booking|bosch|bostik|boston|bot|boutique|box|br|bradesco|bridgestone|broadway|broker|brother|brussels|bs|bt|build|builders|business|buy|buzz|bv|bw|by|bz|bzh|ca|cab|cafe|cal|call|calvinklein|cam|camera|camp|canon|capetown|capital|capitalone|car|caravan|cards|care|career|careers|cars|casa|case|cash|casino|cat|catering|catholic|cba|cbn|cbre|cc|cd|center|ceo|cern|cf|cfa|cfd|cg|ch|chanel|channel|charity|chase|chat|cheap|chintai|christmas|chrome|church|ci|cipriani|circle|cisco|citadel|citi|citic|city|ck|cl|claims|cleaning|click|clinic|clinique|clothing|cloud|club|clubmed|cm|cn|co|coach|codes|coffee|college|cologne|com|commbank|community|company|compare|computer|comsec|condos|construction|consulting|contact|contractors|cooking|cool|coop|corsica|country|coupon|coupons|courses|cpa|cr|credit|creditcard|creditunion|cricket|crown|crs|cruise|cruises|cu|cuisinella|cv|cw|cx|cy|cymru|cyou|cz|dad|dance|data|date|dating|datsun|day|dclk|dds|de|deal|dealer|deals|degree|delivery|dell|deloitte|delta|democrat|dental|dentist|desi|design|dev|dhl|diamonds|diet|digital|direct|directory|discount|discover|dish|diy|dj|dk|dm|dnp|do|docs|doctor|dog|domains|dot|download|drive|dtv|dubai|dupont|durban|dvag|dvr|dz|earth|eat|ec|eco|edeka|edu|education|ee|eg|email|emerck|energy|engineer|engineering|enterprises|epson|equipment|er|ericsson|erni|es|esq|estate|et|eu|eurovision|eus|events|exchange|expert|exposed|express|extraspace|fage|fail|fairwinds|faith|family|fan|fans|farm|farmers|fashion|fast|fedex|feedback|ferrari|ferrero|fi|fidelity|fido|film|final|finance|financial|fire|firestone|firmdale|fish|fishing|fit|fitness|fj|fk|flickr|flights|flir|florist|flowers|fly|fm|fo|foo|food|football|ford|forex|forsale|forum|foundation|fox|fr|free|fresenius|frl|frogans|frontier|ftr|fujitsu|fun|fund|furniture|futbol|fyi|ga|gal|gallery|gallo|gallup|game|games|gap|garden|gay|gb|gbiz|gd|gdn|ge|gea|gent|genting|george|gf|gg|ggee|gh|gi|gift|gifts|gives|giving|gl|glass|gle|global|globo|gm|gmail|gmbh|gmo|gmx|gn|godaddy|gold|goldpoint|golf|goo|goodyear|goog|google|gop|got|gov|gp|gq|gr|grainger|graphics|gratis|green|gripe|grocery|group|gs|gt|gu|gucci|guge|guide|guitars|guru|gw|gy|hair|hamburg|hangout|haus|hbo|hdfc|hdfcbank|health|healthcare|help|helsinki|here|hermes|hiphop|hisamitsu|hitachi|hiv|hk|hkt|hm|hn|hockey|holdings|holiday|homedepot|homegoods|homes|homesense|honda|horse|hospital|host|hosting|hot|hotels|hotmail|house|how|hr|hsbc|ht|hu|hughes|hyatt|hyundai|ibm|icbc|ice|icu|id|ie|ieee|ifm|ikano|il|im|imamat|imdb|immo|immobilien|in|inc|industries|infiniti|info|ing|ink|institute|insurance|insure|int|international|intuit|investments|io|ipiranga|iq|ir|irish|is|ismaili|ist|istanbul|it|itau|itv|jaguar|java|jcb|je|jeep|jetzt|jewelry|jio|jll|jm|jmp|jnj|jo|jobs|joburg|jot|joy|jp|jpmorgan|jprs|juegos|juniper|kaufen|kddi|ke|kerryhotels|kerryproperties|kfh|kg|kh|ki|kia|kids|kim|kindle|kitchen|kiwi|km|kn|koeln|komatsu|kosher|kp|kpmg|kpn|kr|krd|kred|kuokgroup|kw|ky|kyoto|kz|la|lacaixa|lamborghini|lamer|land|landrover|lanxess|lasalle|lat|latino|latrobe|law|lawyer|lb|lc|lds|lease|leclerc|lefrak|legal|lego|lexus|lgbt|li|lidl|life|lifeinsurance|lifestyle|lighting|like|lilly|limited|limo|lincoln|link|live|living|lk|llc|llp|loan|loans|locker|locus|lol|london|lotte|lotto|love|lpl|lplfinancial|lr|ls|lt|ltd|ltda|lu|lundbeck|luxe|luxury|lv|ly|ma|madrid|maif|maison|makeup|man|management|mango|map|market|marketing|markets|marriott|marshalls|mattel|mba|mc|mckinsey|md|me|med|media|meet|melbourne|meme|memorial|men|menu|merckmsd|mg|mh|miami|microsoft|mil|mini|mint|mit|mitsubishi|mk|ml|mlb|mls|mm|mma|mn|mo|mobi|mobile|moda|moe|moi|mom|monash|money|monster|mormon|mortgage|moscow|moto|motorcycles|mov|movie|mp|mq|mr|ms|msd|mt|mtn|mtr|mu|museum|music|mv|mw|mx|my|mz|na|nab|nagoya|name|navy|nba|nc|ne|nec|net|netbank|netflix|network|neustar|new|news|next|nextdirect|nexus|nf|nfl|ng|ngo|nhk|ni|nico|nike|nikon|ninja|nissan|nissay|nl|no|nokia|norton|now|nowruz|nowtv|np|nr|nra|nrw|ntt|nu|nyc|nz|obi|observer|office|okinawa|olayan|olayangroup|ollo|om|omega|one|ong|onl|online|ooo|open|oracle|orange|org|organic|origins|osaka|otsuka|ott|ovh|pa|page|panasonic|paris|pars|partners|parts|party|pay|pccw|pe|pet|pf|pfizer|pg|ph|pharmacy|phd|philips|phone|photo|photography|photos|physio|pics|pictet|pictures|pid|pin|ping|pink|pioneer|pizza|pk|pl|place|play|playstation|plumbing|plus|pm|pn|pnc|pohl|poker|politie|porn|post|pr|praxi|press|prime|pro|prod|productions|prof|progressive|promo|properties|property|protection|pru|prudential|ps|pt|pub|pw|pwc|py|qa|qpon|quebec|quest|racing|radio|re|read|realestate|realtor|realty|recipes|red|redumbrella|rehab|reise|reisen|reit|reliance|ren|rent|rentals|repair|report|republican|rest|restaurant|review|reviews|rexroth|rich|richardli|ricoh|ril|rio|rip|ro|rocks|rodeo|rogers|room|rs|rsvp|ru|rugby|ruhr|run|rw|rwe|ryukyu|sa|saarland|safe|safety|sakura|sale|salon|samsclub|samsung|sandvik|sandvikcoromant|sanofi|sap|sarl|sas|save|saxo|sb|sbi|sbs|sc|scb|schaeffler|schmidt|scholarships|school|schule|schwarz|science|scot|sd|se|search|seat|secure|security|seek|select|sener|services|seven|sew|sex|sexy|sfr|sg|sh|shangrila|sharp|shell|shia|shiksha|shoes|shop|shopping|shouji|show|si|silk|sina|singles|site|sj|sk|ski|skin|sky|skype|sl|sling|sm|smart|smile|sn|sncf|so|soccer|social|softbank|software|sohu|solar|solutions|song|sony|soy|spa|space|sport|spot|sr|srl|ss|st|stada|staples|star|statebank|statefarm|stc|stcgroup|stockholm|storage|store|stream|studio|study|style|su|sucks|supplies|supply|support|surf|surgery|suzuki|sv|swatch|swiss|sx|sy|sydney|systems|sz|tab|taipei|talk|taobao|target|tatamotors|tatar|tattoo|tax|taxi|tc|tci|td|tdk|team|tech|technology|tel|temasek|tennis|teva|tf|tg|th|thd|theater|theatre|tiaa|tickets|tienda|tips|tires|tirol|tj|tjmaxx|tjx|tk|tkmaxx|tl|tm|tmall|tn|to|today|tokyo|tools|top|toray|toshiba|total|tours|town|toyota|toys|tr|trade|trading|training|travel|travelers|travelersinsurance|trust|trv|tt|tube|tui|tunes|tushu|tv|tvs|tw|tz|ua|ubank|ubs|ug|uk|unicom|university|uno|uol|ups|us|uy|uz|va|vacations|vana|vanguard|vc|ve|vegas|ventures|verisign|versicherung|vet|vg|vi|viajes|video|vig|viking|villas|vin|vip|virgin|visa|vision|viva|vivo|vlaanderen|vn|vodka|volvo|vote|voting|voto|voyage|vu|wales|walmart|walter|wang|wanggou|watch|watches|weather|weatherchannel|webcam|weber|website|wed|wedding|weibo|weir|wf|whoswho|wien|wiki|williamhill|win|windows|wine|winners|wme|wolterskluwer|woodside|work|works|world|wow|ws|wtc|wtf|xbox|xerox|xihuan|xin|xn--11b4c3d|xn--1ck2e1b|xn--1qqw23a|xn--2scrj9c|xn--30rr7y|xn--3bst00m|xn--3ds443g|xn--3e0b707e|xn--3hcrj9c|xn--3pxu8k|xn--42c2d9a|xn--45br5cyl|xn--45brj9c|xn--45q11c|xn--4dbrk0ce|xn--4gbrim|xn--54b7fta0cc|xn--55qw42g|xn--55qx5d|xn--5su34j936bgsg|xn--5tzm5g|xn--6frz82g|xn--6qq986b3xl|xn--80adxhks|xn--80ao21a|xn--80aqecdr1a|xn--80asehdb|xn--80aswg|xn--8y0a063a|xn--90a3ac|xn--90ae|xn--90ais|xn--9dbq2a|xn--9et52u|xn--9krt00a|xn--b4w605ferd|xn--bck1b9a5dre4c|xn--c1avg|xn--c2br7g|xn--cck2b3b|xn--cckwcxetd|xn--cg4bki|xn--clchc0ea0b2g2a9gcd|xn--czr694b|xn--czrs0t|xn--czru2d|xn--d1acj3b|xn--d1alf|xn--e1a4c|xn--eckvdtc9d|xn--efvy88h|xn--fct429k|xn--fhbei|xn--fiq228c5hs|xn--fiq64b|xn--fiqs8s|xn--fiqz9s|xn--fjq720a|xn--flw351e|xn--fpcrj9c3d|xn--fzc2c9e2c|xn--fzys8d69uvgm|xn--g2xx48c|xn--gckr3f0f|xn--gecrj9c|xn--gk3at1e|xn--h2breg3eve|xn--h2brj9c|xn--h2brj9c8c|xn--hxt814e|xn--i1b6b1a6a2e|xn--imr513n|xn--io0a7i|xn--j1aef|xn--j1amh|xn--j6w193g|xn--jlq480n2rg|xn--jvr189m|xn--kcrx77d1x4a|xn--kprw13d|xn--kpry57d|xn--kput3i|xn--l1acc|xn--lgbbat1ad8j|xn--mgb9awbf|xn--mgba3a3ejt|xn--mgba3a4f16a|xn--mgba7c0bbn0a|xn--mgbaam7a8h|xn--mgbab2bd|xn--mgbah1a3hjkrd|xn--mgbai9azgqp6j|xn--mgbayh7gpa|xn--mgbbh1a|xn--mgbbh1a71e|xn--mgbc0a9azcg|xn--mgbca7dzdo|xn--mgbcpq6gpa1a|xn--mgberp4a5d4ar|xn--mgbgu82a|xn--mgbi4ecexp|xn--mgbpl2fh|xn--mgbt3dhd|xn--mgbtx2b|xn--mgbx4cd0ab|xn--mix891f|xn--mk1bu44c|xn--mxtq1m|xn--ngbc5azd|xn--ngbe9e0a|xn--ngbrx|xn--node|xn--nqv7f|xn--nqv7fs00ema|xn--nyqy26a|xn--o3cw4h|xn--ogbpf8fl|xn--otu796d|xn--p1acf|xn--p1ai|xn--pgbs0dh|xn--pssy2u|xn--q7ce6a|xn--q9jyb4c|xn--qcka1pmc|xn--qxa6a|xn--qxam|xn--rhqv96g|xn--rovu88b|xn--rvc1e0am3e|xn--s9brj9c|xn--ses554g|xn--t60b56a|xn--tckwe|xn--tiq49xqyj|xn--unup4y|xn--vermgensberater-ctb|xn--vermgensberatung-pwb|xn--vhquv|xn--vuq861b|xn--w4r85el8fhu5dnra|xn--w4rs40l|xn--wgbh1c|xn--wgbl6a|xn--xhq521b|xn--xkc2al3hye2a|xn--xkc2dl3a5ee0h|xn--y9a3aq|xn--yfro4i67o|xn--ygbi2ammx|xn--zfr164b|xxx|xyz|yachts|yahoo|yamaxun|yandex|ye|yodobashi|yoga|yokohama|you|youtube|yt|yun|za|zappos|zara|zero|zip|zm|zone|zuerich|zw)\b(?:[/?#](?:[a-zA-Z0-9\-._~:/?#\[\]@!$&\'()*+,;=%]|(?:%[0-9A-Fa-f]{2}))*)?'
    r')',
    re.IGNORECASE | re.MULTILINE
)

def parse_content_with_links(text: str) -> List[Tuple[str, Optional[str]]]:
    """
    Parse content and identify links.
    Returns list of tuples: (text, url or None)

    Example:
        "Check this https://example.com for info"
        -> [("Check this ", None), ("https://example.com", "https://example.com"), (" for info", None)]
    """
    if not text:
        return [(text, None)]

    segments = []
    last_end = 0

    for match in URL_PATTERN.finditer(text):
        # Add text before the URL
        if match.start() > last_end:
            segments.append((text[last_end:match.start()], None))

        # Add the URL itself
        url = match.group(0)
        # Ensure URL has protocol
        if not url.startswith(('http://', 'https://', 'ftp://')):
            if url.startswith('www.'):
                url = 'https://' + url
            else:
                url = 'https://' + url

        segments.append((match.group(0), url))
        last_end = match.end()

    # Add remaining text
    if last_end < len(text):
        segments.append((text[last_end:], None))

    return segments

# Create a buffer to capture logs
_log_buffer = StringIO()


class CollapsibleOptionList(OptionList):
    """OptionList with collapsible folders."""
    
    class ItemSelected(Message):
        """Posted when an item is selected."""
        def __init__(self, item_type: str, item_data: dict) -> None:
            super().__init__()
            self.item_type = item_type
            self.item_data = item_data

    class MouseScroll(Message):
        """Posted when mouse scrolls up or down."""
        def __init__(self, direction: str) -> None:
            super().__init__()
            self.direction = direction  # "up" or "down"

    DEFAULT_CSS = """
    CollapsibleOptionList {
        width: 35;
        height: 100%;
        background: $surface;
        /* Disable smooth scrolling - use keyboard navigation instead */
        overflow-y: hidden;
    }
    """
    
    def __init__(self, database=None, **kwargs):
        super().__init__(**kwargs)
        self.dms_data: List[dict] = []
        self.guilds_data: List[dict] = []
        self.favorites: Set[str] = set()
        self.database = database  # Reference to database for persisting favorites

        # Load favorites from database on initialization
        if self.database:
            self.favorites = self.database.load_favorites()

        # Folder states
        self.folders_open = {
            'favorites': True,
            'dms': True,
            'guilds': True,
        }

        # Guild expanded states and channels
        self.guild_expanded = {}  # guild_id -> bool
        self.guild_channels = {}  # guild_id -> list of channels

        self.all_items: List[Tuple[str, dict]] = []

        # Debouncing for smooth rendering during heavy loading
        self.rebuild_timer = None  # Timer for debounced rebuild

        # Track item to preserve cursor on during rebuild (e.g., when toggling folders)
        self.preserve_cursor_item = None

    def action_scroll_down(self) -> None:
        """Handle scroll down - move cursor down one item like arrow key."""
        if self.option_count > 0:
            current = self.highlighted_index if self.highlighted_index is not None else -1
            next_idx = min(current + 1, self.option_count - 1)
            self.highlighted_index = next_idx

    def action_scroll_up(self) -> None:
        """Handle scroll up - move cursor up one item like arrow key."""
        if self.option_count > 0:
            current = self.highlighted_index if self.highlighted_index is not None else 0
            prev_idx = max(current - 1, 0)
            self.highlighted_index = prev_idx

    def on_scroll_down(self) -> None:
        """Handle mouse scroll down - move cursor down one item."""
        self.action_scroll_down()

    def on_scroll_up(self) -> None:
        """Handle mouse scroll up - move cursor up one item."""
        self.action_scroll_up()

    def _get_channel_icon(self, channel: dict) -> str:
        """Get icon for channel type."""
        channel_type = channel.get('type', 0)
        # Discord channel types: 0=text, 2=voice, 4=category, 11=thread, 12=thread (public), 13=thread (private)
        if channel_type == 4:
            return "📁"  # Category
        elif channel_type in [11, 12, 13]:
            return "🧵"  # Thread
        elif channel_type == 2:
            return "🔊"  # Voice
        else:
            return "#"   # Text

    def _sort_channels(self, channels: List[dict]) -> tuple:
        """Sort channels: unparented first, then categories with children."""
        unparented = []
        categories = {}
        categorized = []

        for ch in channels:
            if ch.get('type') == 4:  # Category
                categories[ch.get('id')] = ch
            elif not ch.get('parent_id'):  # No parent
                unparented.append(ch)
            else:
                categorized.append(ch)

        # Sort by position
        unparented.sort(key=lambda x: x.get('position', 0))
        categorized.sort(key=lambda x: x.get('position', 0))

        result = unparented.copy()

        # Add categories with their children
        for cat_id, category in categories.items():
            result.append(category)
            # Add children of this category
            children = [ch for ch in categorized if ch.get('parent_id') == cat_id]
            children.sort(key=lambda x: x.get('position', 0))
            result.extend(children)

        return result

    def rebuild_list_debounced(self) -> None:
        """Queue a rebuild with debouncing to avoid excessive re-renders during heavy loading.

        Multiple calls within 200ms will be batched into a single rebuild. This prevents
        lag and cursor flashing when channels/members are being loaded rapidly.
        """
        # Cancel existing timer if any
        if self.rebuild_timer is not None:
            self.rebuild_timer.stop()

        # Schedule rebuild after 200ms
        def do_rebuild() -> None:
            self.rebuild_list()

        self.rebuild_timer = self.set_timer(0.2, callback=do_rebuild)

    def rebuild_list(self) -> None:
        """Rebuild the OptionList based on current state."""
        # Determine which item to preserve cursor on
        selected_item_data = None

        # If we have an explicit item to preserve (e.g., toggled folder), use that
        if self.preserve_cursor_item is not None:
            selected_item_data = self.preserve_cursor_item
            self.preserve_cursor_item = None  # Clear after using
        # Otherwise, try to keep the current selection
        elif hasattr(self, 'highlighted_index') and self.highlighted_index is not None and self.highlighted_index < len(self.all_items):
            selected_item_data = self.all_items[self.highlighted_index]

        self.clear_options()
        self.all_items = []
        width = 28

        # Helper to format items
        def format_item(name: str, is_favorite: bool = False) -> str:
            available = width - 6
            if len(name) > available:
                name = name[:available - 1] + "…"
            star = "★" if is_favorite else " "
            return f"╰──{name:<{available - 2}}{star}"

        def format_folder(name: str, is_open: bool) -> str:
            arrow = "▼" if is_open else "▶"
            available = width - 4
            return f"{arrow} {name:<{available - 2}}"

        def format_channel(name: str, icon: str, indent: int = 1) -> str:
            """Format channel with icon and indentation."""
            indent_str = "  " * indent
            available = width - len(indent_str) - 3
            if len(name) > available:
                name = name[:available - 1] + "…"
            return f"{indent_str}├─{icon} {name}"

        def format_category(name: str) -> str:
            """Format category channel."""
            available = width - 4
            if len(name) > available:
                name = name[:available - 1] + "…"
            return f"  ├─📁 {name}"
        
        # FAVORITES
        fav_label = format_folder("Favorites", self.folders_open['favorites'])
        self.add_option(fav_label)
        self.all_items.append(('folder', {'id': 'favorites', 'name': 'Favorites'}))
        
        if self.folders_open['favorites']:
            for dm in self.dms_data:
                if dm['id'] in self.favorites:
                    name = dm.get('display_name') or 'Unknown'
                    label = "  " + format_item(name, True)
                    self.add_option(label)
                    self.all_items.append(('dm', dm))
            
            for guild in self.guilds_data:
                if guild['id'] in self.favorites:
                    name = guild.get('name', 'Unknown')
                    label = "  " + format_item(name, True)
                    self.add_option(label)
                    self.all_items.append(('guild', guild))
        
        # DMS
        dms_label = format_folder("Direct Messages", self.folders_open['dms'])
        self.add_option(dms_label)
        self.all_items.append(('folder', {'id': 'dms', 'name': 'Direct Messages'}))
        
        if self.folders_open['dms']:
            for dm in self.dms_data:
                if dm['id'] not in self.favorites:
                    name = dm.get('display_name') or 'Unknown'
                    label = "  " + format_item(name, False)
                    self.add_option(label)
                    self.all_items.append(('dm', dm))
        
        # GUILDS
        guilds_label = format_folder("Guilds", self.folders_open['guilds'])
        self.add_option(guilds_label)
        self.all_items.append(('folder', {'id': 'guilds', 'name': 'Guilds'}))

        if self.folders_open['guilds']:
            for guild in self.guilds_data:
                if guild['id'] not in self.favorites:
                    guild_id = guild['id']
                    name = guild.get('name', 'Unknown')

                    # Guild with expand/collapse indicator
                    is_expanded = self.guild_expanded.get(guild_id, False)
                    arrow = "▼" if is_expanded else "▶"
                    label = f"  {arrow} {name[:22]}"
                    self.add_option(label)
                    self.all_items.append(('guild', guild))

                    # Show channels if guild is expanded
                    if is_expanded and guild_id in self.guild_channels:
                        channels = self._sort_channels(self.guild_channels[guild_id])
                        for channel in channels:
                            ch_id = channel.get('id')
                            ch_name = channel.get('name', 'Unknown')
                            ch_type = channel.get('type', 0)
                            parent_id = channel.get('parent_id')

                            # Skip channels that are children of categories (they're shown under categories)
                            if parent_id and any(c.get('id') == parent_id and c.get('type') == 4 for c in channels):
                                continue

                            icon = self._get_channel_icon(channel)

                            if ch_type == 4:  # Category
                                label = format_category(ch_name)
                                self.add_option(label)
                                self.all_items.append(('category', channel))

                                # Show channels under this category
                                for child in channels:
                                    if child.get('parent_id') == ch_id:
                                        child_name = child.get('name', 'Unknown')
                                        child_icon = self._get_channel_icon(child)
                                        label = format_channel(child_name, child_icon, indent=2)
                                        self.add_option(label)
                                        self.all_items.append(('channel', child))
                            else:
                                # Regular channel (no parent or parent not a category)
                                label = format_channel(ch_name, icon, indent=1)
                                self.add_option(label)
                                self.all_items.append(('channel', channel))

        # Restore selection after rebuild
        if selected_item_data is not None:
            item_type, item_data = selected_item_data
            # Find the item with matching ID in the rebuilt list
            for idx, (current_item_type, current_item_data) in enumerate(self.all_items):
                if (current_item_type == item_type and
                    current_item_data.get('id') == item_data.get('id')):
                    self.highlighted_index = idx
                    break

    def populate_from_data(self, dms_list: List[dict], guilds_list: List[dict]) -> None:
        """Populate from data."""
        self.dms_data = dms_list
        self.guilds_data = guilds_list
        self.rebuild_list()

    def set_guild_channels(self, guild_id: str, channels: List[dict]) -> None:
        """Set channels for a guild and queue a debounced rebuild.

        Uses debouncing to prevent excessive re-renders when multiple guilds
        are loading channels simultaneously.
        """
        self.guild_channels[guild_id] = channels
        self.rebuild_list_debounced()
    
    def on_option_list_option_selected(self, message: OptionList.OptionSelected) -> None:
        """Handle selection - toggle folder/guild or select item."""
        idx = message.option_index
        if idx < len(self.all_items):
            item_type, item_data = self.all_items[idx]

            if item_type == 'folder':
                # Toggle folder - preserve cursor on this folder after rebuild
                folder_id = item_data['id']
                self.folders_open[folder_id] = not self.folders_open[folder_id]
                # Set the folder to be preserved so cursor stays on it
                self.preserve_cursor_item = (item_type, item_data)
                self.rebuild_list()
            elif item_type == 'guild':
                # Toggle guild expansion - preserve cursor on this guild after rebuild
                guild_id = item_data.get('id')
                if guild_id:
                    current_state = self.guild_expanded.get(guild_id, False)
                    self.guild_expanded[guild_id] = not current_state

                    # If expanding, fetch channels for this guild
                    if not current_state and guild_id not in self.guild_channels:
                        # Request channels from app
                        self.post_message(self.ItemSelected('guild_expand', item_data))
                    else:
                        # Set the guild to be preserved so cursor stays on it
                        self.preserve_cursor_item = (item_type, item_data)
                        self.rebuild_list()
            else:
                # Select channel, dm, or category
                self.post_message(self.ItemSelected(item_type, item_data))
    
    def toggle_favorite(self) -> None:
        """Toggle favorite for selected item and save to database."""
        if hasattr(self, 'highlighted_index') and self.highlighted_index is not None:
            idx = self.highlighted_index
            if idx < len(self.all_items):
                item_type, item_data = self.all_items[idx]
                if item_type in ('dm', 'guild'):
                    item_id = item_data.get('id')
                    item_name = item_data.get('name') or item_data.get('display_name', 'Unknown')
                    if item_id:
                        if item_id in self.favorites:
                            # Remove from favorites
                            self.favorites.discard(item_id)
                            # Save to database
                            if self.database:
                                self.database.remove_favorite(item_id)
                        else:
                            # Add to favorites
                            self.favorites.add(item_id)
                            # Save to database
                            if self.database:
                                self.database.add_favorite(item_id, item_type, item_name)
                        # Preserve cursor on this item when toggling favorite
                        self.preserve_cursor_item = (item_type, item_data)
                        self.rebuild_list()


class MessageItemWidget(Static):
    """Widget to display a single message with timestamp, author, and content."""

    DEFAULT_CSS = """
    MessageItemWidget {
        width: 1fr;
        height: auto;
        padding: 0 1;
    }
    """

    def __init__(self, message: dict, container_width: int = 80, is_grouped: bool = False, **kwargs):
        super().__init__(**kwargs)
        self.message = message
        self.container_width = container_width
        self.is_grouped = is_grouped  # True if this message follows same author

    def _get_relative_timestamp(self, iso_timestamp: str) -> str:
        """Convert ISO timestamp to relative time (e.g., '5 min ago')."""
        from datetime import datetime
        try:
            msg_time = datetime.fromisoformat(iso_timestamp.replace('Z', '+00:00'))
            now = datetime.now(msg_time.tzinfo)
            delta = now - msg_time

            seconds = int(delta.total_seconds())
            if seconds < 60:
                return "now"
            elif seconds < 3600:
                mins = seconds // 60
                return f"{mins}m" if mins == 1 else f"{mins}m"
            elif seconds < 86400:
                hours = seconds // 3600
                return f"{hours}h" if hours == 1 else f"{hours}h"
            else:
                days = seconds // 86400
                return f"{days}d" if days == 1 else f"{days}d"
        except:
            return iso_timestamp

    def render(self) -> Text:
        """Render the message with timestamp, author, and content."""
        msg = self.message

        # Get message metadata
        timestamp = msg.get('timestamp', '')
        relative_time = self._get_relative_timestamp(timestamp)
        author = msg.get('author', {})
        author_id = author.get('id', '')
        author_name = author.get('global_name') or author.get('username', 'Unknown')
        user_color = msg.get('author_color', '#5865F2')
        content = msg.get('content', '')

        # Build result as list of lines
        result_lines = []

        if not content:
            # Empty message - just show timestamp and author (unless grouped)
            if not self.is_grouped:
                message = Text()
                message.append(relative_time, style="dim")
                message.append(" ")
                message.append(author_name, style=f"bold {user_color}")
                message.append(": ")
                result_lines.append(message)
        else:
            # Calculate available width for content
            # If grouped, use full width. Otherwise account for header
            if self.is_grouped:
                available_width = self.container_width - 8  # Small indent for grouped messages
                indent = "    "
            else:
                prefix_width = len(relative_time) + 1 + len(author_name) + 2
                available_width = self.container_width - prefix_width
                indent = ""

            if available_width < 20:
                available_width = self.container_width - 8
                indent = "    "

            # Handle multiline content
            paragraphs = content.split('\n')

            for para_idx, paragraph in enumerate(paragraphs):
                # Wrap paragraph
                wrapped_lines = self._wrap_text(paragraph, available_width) if available_width > 0 else [paragraph]

                for line_idx, line in enumerate(wrapped_lines):
                    message = Text()

                    # Add timestamp/author on first line only (if not grouped)
                    if not self.is_grouped and para_idx == 0 and line_idx == 0:
                        message.append(relative_time, style="dim")
                        message.append(" ")
                        message.append(author_name, style=f"bold {user_color}")
                        message.append(": ")
                    else:
                        # Continuation lines or grouped messages - indent
                        message.append(indent if indent else "    " * 2)

                    # Parse content for links
                    self._append_content_with_links(message, line)
                    result_lines.append(message)

        # Combine all lines into single Text object
        if result_lines:
            combined = result_lines[0]
            for line in result_lines[1:]:
                combined.append("\n")
                combined.append_text(line)
            return combined
        return Text("")

    def _wrap_text(self, text: str, max_width: int) -> List[str]:
        """Wrap text to max_width."""
        if max_width <= 0:
            return [text]

        from textwrap import wrap

        lines = []
        for paragraph in text.split('\n'):
            if not paragraph:
                lines.append('')
            else:
                wrapped_lines = wrap(paragraph, width=max_width, break_long_words=True, break_on_hyphens=False)
                lines.extend(wrapped_lines if wrapped_lines else [''])

        return lines if lines else ['']

    def _append_content_with_links(self, text_obj: Text, content: str) -> None:
        """Append content to Text object with link styling."""
        segments = parse_content_with_links(content)

        for segment_text, url in segments:
            if url:
                text_obj.append(segment_text, style=f"#0066FF bold underline link {url}")
            else:
                text_obj.append(segment_text)


class DateDividerItem(Static):
    """Widget to display a date divider between messages."""

    DEFAULT_CSS = """
    DateDividerItem {
        width: 1fr;
        height: auto;
        padding: 0 1;
    }
    """

    def __init__(self, date_str: str, **kwargs):
        super().__init__(**kwargs)
        self.date_str = date_str

    def render(self) -> Text:
        """Render the date divider."""
        try:
            from datetime import datetime as dt
            date_obj = dt.fromisoformat(self.date_str)
            formatted_date = date_obj.strftime('%A, %B %d, %Y')
        except:
            formatted_date = self.date_str

        divider = Text()
        divider.append('─' * 12, style='dim')
        divider.append(' ', style='dim')
        divider.append(formatted_date, style='bold dim')
        divider.append(' ', style='dim')
        divider.append('─' * 12, style='dim')
        return divider


class MessagesPanel(Static):
    """Panel displaying messages as interactive list items."""

    DEFAULT_CSS = """
    MessagesPanel {
        width: 1fr;
        height: 1fr;
        overflow: auto;
    }

    #messages-list {
        width: 1fr;
        height: 1fr;
        scrollbar-size: 1 1;
    }

    #messages-list ListItem {
        padding: 0 1;
        border: none;
    }

    #messages-list > ListItem:focus {
        background: $accent;
    }
    """

    BINDINGS = [
        Binding("ctrl+o", "open_link", "Open Link"),
    ]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.current_channel = None
        self.messages_data = []
        self.messages_list = None
        self.container_width = 80  # Default fallback

        # Lazy loading state
        self.oldest_message_id = None
        self.has_more_messages = True
        self.is_loading = False
        self.app_ref = None  # Reference to parent app for API calls

        # Scroll position tracking
        self.last_scroll_y = 0

    def compose(self) -> ComposeResult:
        yield ListView(id="messages-list")

    def on_mount(self):
        self.messages_list = self.query_one("#messages-list", ListView)
        self._update_container_width()

        # Display initial empty state
        empty_item = ListItem(Static("[dim]Select a channel to view messages[/dim]"))
        self.messages_list.append(empty_item)

        # Watch ListView scroll position for lazy loading
        self.watch(self.messages_list, "scroll_y", self._on_list_scroll)

        # Store reference to app for opening URLs
        self.app_instance = self.app

    def action_open_link(self) -> None:
        """Open the most recent link found in messages."""
        # Find first URL in the current message content (searching from newest to oldest)
        if self.messages_data:
            for msg in reversed(self.messages_data):
                content = msg.get('content', '')
                url_match = URL_PATTERN.search(content)
                if url_match:
                    url = url_match.group(0)
                    # Ensure protocol is present
                    if not url.startswith(('http://', 'https://', 'ftp://')):
                        if url.startswith('www.'):
                            url = 'https://' + url
                        else:
                            url = 'https://' + url
                    # Open the URL
                    try:
                        import webbrowser
                        logger.info(f"Opening URL via Ctrl+O: {url}")
                        webbrowser.open(url)
                    except Exception as e:
                        logger.error(f"Failed to open URL {url}: {e}")
                    return
        else:
            logger.debug("No messages to search for links")

    def _on_list_scroll(self, old_scroll_y: int, new_scroll_y: int) -> None:
        """Handle List scroll - direct and efficient."""
        # Enforce 3-line minimum margin from top
        if new_scroll_y < 18:
            self.messages_list.scroll_y = 18
            return

        self.last_scroll_y = new_scroll_y

        # Trigger lazy load immediately when scrolling up near top - no delays
        if (new_scroll_y - old_scroll_y < 0 and new_scroll_y < 150 and
            not self.is_loading and self.has_more_messages and self.app_ref and self.oldest_message_id):
            asyncio.create_task(self._trigger_lazy_load())

    async def _trigger_lazy_load(self) -> None:
        """Trigger loading of older messages."""
        if self.is_loading or not self.has_more_messages or not self.app_ref or not self.oldest_message_id:
            return

        self.is_loading = True
        await self.app_ref._load_older_messages(self.current_channel, self.oldest_message_id)

    def _update_container_width(self) -> int:
        """Get the actual available width for messages in characters."""
        try:
            # Get the container's inner width in cells
            if self.messages_list:
                container_width = self.messages_list.size.width
                if container_width > 0:
                    self.container_width = container_width - 2  # Account for padding/borders
                    return self.container_width
        except:
            pass
        return self.container_width

    def on_resize(self) -> None:
        """Handle terminal resize - reflow messages."""
        self._update_container_width()
        # Reflow messages if we have any
        if self.messages_data and self.current_channel:
            self.display_messages(self.messages_data, self.current_channel)

    def _measure_text_width(self, text: str) -> int:
        """Measure the visual width of text (excluding ANSI codes)."""
        from rich.console import Console
        console = Console()
        # Use Rich's length measurement which accounts for ANSI codes
        return console.measure(text).maximum

    def _wrap_text(self, text: str, max_width: int) -> List[str]:
        """
        Wrap text to max_width, accounting for word boundaries.
        Returns list of wrapped lines.
        """
        if max_width <= 0:
            return [text]

        from textwrap import wrap

        lines = []
        for paragraph in text.split('\n'):
            if not paragraph:
                lines.append('')
            else:
                # Use Python's textwrap for reliable word wrapping
                wrapped_lines = wrap(paragraph, width=max_width, break_long_words=True, break_on_hyphens=False)
                lines.extend(wrapped_lines if wrapped_lines else [''])

        return lines if lines else ['']

    def _append_content_with_links(self, text_obj: Text, content: str) -> None:
        """
        Append content to a Rich Text object, parsing and styling links.
        Links are displayed in blue with underline and are clickable via OSC 8 and webbrowser.
        """
        segments = parse_content_with_links(content)

        for segment_text, url in segments:
            if url:
                # This is a link - style it with:
                # - #0066FF: Bright blue color for links
                # - underline: Standard link visual indicator
                # - link:{url}: OSC 8 hyperlink for terminals that support it
                # - bold: Make links stand out more
                # Also store the URL in metadata for programmatic opening
                text_obj.append(segment_text, style=f"#0066FF bold underline link {url}")
            else:
                # Regular text - append as-is
                text_obj.append(segment_text)

    def _open_url(self, url: str) -> None:
        """Open a URL in the default web browser."""
        try:
            # Add protocol if missing
            if not url.startswith(('http://', 'https://', 'ftp://')):
                url = 'https://' + url

            logger.info(f"Opening URL: {url}")
            webbrowser.open(url)
        except Exception as e:
            logger.error(f"Failed to open URL {url}: {e}")
            if self.status_panel:
                self._update_status(f"[red]Failed to open link: {e}[/red]")

    def clear_messages(self):
        """Clear the message display."""
        if self.messages_list:
            self.messages_list.clear()
        self.messages_data = []

    def display_messages(self, messages: List[dict], channel_data: dict, app_ref=None, prepend: bool = False):
        """Display messages for a channel. If prepend=True, add to beginning (efficient cursor-preserving update)."""
        if not prepend:
            # New channel - reset pagination state
            self.clear_messages()
            self.current_channel = channel_data
            self.messages_data = messages
            self.is_loading = False
            self.has_more_messages = True
        else:
            # Lazy loading - prepend to existing messages
            self.messages_data = messages + self.messages_data

        # Store app reference for future API calls
        if app_ref:
            self.app_ref = app_ref

        # Track oldest message ID
        if messages:
            self.oldest_message_id = messages[0].get('id')  # First message (oldest) after sorting

        # Display messages
        if self.messages_list:
            if prepend:
                # EFFICIENT PREPEND: Insert new messages at top, preserve cursor index
                # Save cursor position and scroll to restore later
                saved_index = self.messages_list.index
                saved_cursor_is_visible = saved_index is not None and saved_index >= 0

                # Build new items from prepended messages (in reverse order)
                new_items = []
                current_date = None
                previous_author_id = None
                for msg in reversed(messages):
                    msg_date = msg.get('date', '')
                    author = msg.get('author', {})
                    current_author_id = author.get('id', '')

                    # Add date divider if date changed
                    if msg_date and msg_date != current_date:
                        current_date = msg_date
                        divider_widget = DateDividerItem(msg_date)
                        new_items.append(ListItem(divider_widget))
                        previous_author_id = None  # Reset grouping after date divider

                    # Detect if this message is grouped
                    is_grouped = previous_author_id == current_author_id and previous_author_id is not None
                    previous_author_id = current_author_id

                    # Add message item with grouping info
                    message_widget = MessageItemWidget(msg, self.container_width, is_grouped=is_grouped)
                    new_items.append(ListItem(message_widget))

                # Insert all new items at position 0 (top of list)
                # ListView.insert() takes (index, items_iterable) - pass list directly
                if new_items:
                    self.messages_list.insert(0, new_items)
                    # Don't restore cursor position when prepending - insert() is async
                    # and we can't safely set index until insert completes
                    # Instead, let cursor stay at top to show newly loaded messages
                    # The user can scroll down to see the previous cursor position
            else:
                # Initial load - full rebuild is fine for new channel
                self.messages_list.clear()
                self._render_messages_with_dividers(messages)
                # Scroll to bottom for new channels - keep cursor at end
                if self.messages_list:
                    self.messages_list.index = len(self.messages_list) - 1
                    self.messages_list.scroll_visible(animate=False)

    def _render_messages_with_dividers(self, messages: List[dict]) -> None:
        """Render messages with date dividers and smart grouping (efficient batch append)."""
        if not self.messages_list:
            return

        # Build items in batch then extend all at once (more efficient than individual appends)
        items_to_add = []
        current_date = None
        previous_author_id = None

        for msg in reversed(messages):
            msg_date = msg.get('date', '')
            author = msg.get('author', {})
            current_author_id = author.get('id', '')

            # Check if date changed - add divider if so
            if msg_date and msg_date != current_date:
                current_date = msg_date
                divider_widget = DateDividerItem(msg_date)
                items_to_add.append(ListItem(divider_widget))
                previous_author_id = None  # Reset grouping after date divider

            # Detect if this message is grouped (same author as previous)
            is_grouped = previous_author_id == current_author_id and previous_author_id is not None
            previous_author_id = current_author_id

            # Add message item widget with grouping info
            message_widget = MessageItemWidget(msg, self.container_width, is_grouped=is_grouped)
            items_to_add.append(ListItem(message_widget))

        # Batch append all items at once (single operation vs many)
        self.messages_list.extend(items_to_add)

class InputPanel(Static):
    """Panel for composing and sending messages."""

    DEFAULT_CSS = """
    InputPanel {
        height: auto;
        border: heavy $accent;
        padding: 1;
    }

    InputPanel > Input {
        width: 1fr;
        margin: 0;
    }
    """

    def __init__(self, app_ref=None, **kwargs):
        super().__init__(**kwargs)
        self.app_ref = app_ref

    def compose(self) -> ComposeResult:
        """Compose the input panel with text input field."""
        yield Input(
            placeholder="Type a message... (Enter to send)",
            id="message-input"
        )

    async def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle message submission when user presses Enter."""
        content = event.value.strip()
        if not content:
            return

        # Get the input field and clear it for next message
        try:
            input_field = self.query_one("#message-input", Input)
            input_field.value = ""
        except Exception as e:
            logger.warning(f"Failed to clear input field: {e}")

        # Send the message asynchronously
        if self.app_ref:
            await self.app_ref._send_message(content)
        else:
            logger.error("InputPanel has no app_ref - cannot send message")


class StatusPanel(Static):
    """Status bar at bottom."""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.status_text = "[bold]Ready[/bold] | ↑↓: Navigate, Enter: Select/Expand, *: Favorite, Ctrl+C: Quit"
    
    def render(self) -> str:
        return self.status_text
    
    def update_status(self, message: str) -> None:
        """Update status text."""
        self.status_text = message
        self.refresh()


class DiscordoApp(App):
    """Main Discordo application."""
    
    TITLE = "Discordo - Discord TUI Client"
    
    CSS = """
    Screen {
        background: $surface;
    }
    
    #guilds-panel {
        width: 35;
        height: 100%;
    }
    
    #messages-panel {
        width: 1fr;
        height: 1fr;
    }
    
    #input-panel {
        width: 1fr;
        height: 8;
    }
    
    #status-panel {
        dock: bottom;
        height: 1;
        background: $panel;
    }
    """
    
    BINDINGS = [
        Binding("ctrl+c", "quit", "Quit"),
        Binding("ctrl+d", "logout", "Logout"),
        Binding("up", "move_up", "Up"),
        Binding("down", "move_down", "Down"),
        Binding("enter", "select_item", "Select"),
        Binding("f", "toggle_favorite", "Star"),
    ]

    def __init__(self, cfg: Config):
        """Initialize the application."""
        super().__init__()
        self.cfg = cfg
        self.gateway: Optional[DiscordGateway] = None
        self.guilds_panel: Optional[CollapsibleOptionList] = None
        self.messages_panel: Optional[MessagesPanel] = None
        self.status_panel: Optional[StatusPanel] = None
        self.is_logged_in = False
        self.current_channel: Optional[dict] = None  # Currently selected channel
        self.token: Optional[str] = None  # User's Discord token

        # Initialize database for caching messages
        self.db = DiscordDatabase(Path.home() / '.cache' / 'discordo')

        # Track the currently active/selected item in the guilds panel
        self.active_guild_item = None  # (item_type, item_data) tuple or None
    
    def compose(self) -> ComposeResult:
        """Compose the app layout."""
        # Create guilds panel with database for favorite persistence
        guilds_panel = CollapsibleOptionList(database=self.db, id="guilds-panel")
        self.guilds_panel = guilds_panel

        # Main layout with guilds on left and messages/input on right
        with Horizontal():
            yield guilds_panel
            with Vertical():
                yield MessagesPanel(id="messages-panel")
                yield InputPanel(app_ref=self, id="input-panel")

        # Status bar at bottom
        status_panel = StatusPanel(id="status-panel")
        self.status_panel = status_panel
        yield status_panel
    
    def on_mount(self) -> None:
        """App mounted - check for token and login."""
        self._update_status("[yellow]Checking for token...[/yellow]")
        # Set focus to guilds panel so it receives key events
        if self.guilds_panel:
            self.set_focus(self.guilds_panel)
        asyncio.create_task(self._check_and_login())
    
    def on_collapsible_option_list_item_selected(self, message: CollapsibleOptionList.ItemSelected) -> None:
        """Handle item selection from guilds list."""
        # Track the active item for starring/favoriting
        # Only track guild and dm items, not folders or channels
        if message.item_type in ('guild', 'dm'):
            self.active_guild_item = (message.item_type, message.item_data)

        if message.item_type == 'guild_expand':
            # Fetch channels for this guild
            asyncio.create_task(self._load_guild_channels(message.item_data))
        elif message.item_type == 'channel':
            # Load messages for this channel
            asyncio.create_task(self._load_channel_messages(message.item_data))
        elif message.item_type in ('dm', 'guild'):
            # Load messages for DM or default guild view
            asyncio.create_task(self._load_channel_messages(message.item_data))
    
    async def _check_and_login(self) -> None:
        """Check for token and attempt login."""
        import keyring
        from discordo.internal.consts import DISCORDO_NAME
        
        # Try to get token from keyring
        token = None
        try:
            token = keyring.get_password(DISCORDO_NAME, 'token')
            if token:
                logger.info("Token found in keyring")
        except Exception as e:
            logger.debug(f"Could not get token from keyring: {e}")
        
        if token:
            # First, load from cache (instant display)
            self._load_from_cache()
            # Then connect to Discord to refresh
            await self.connect_discord(token)
        else:
            self._update_status("[yellow]No token found - use: python3 main.py --token YOUR_TOKEN[/yellow]")
    
    def _load_from_cache(self) -> None:
        """Load guilds and DMs from local cache (instant display)."""
        try:
            if not self.guilds_panel:
                return
            
            # Load DMs from cache
            dms_list = []
            cached_dms = self.db.get_dms()
            for dm in cached_dms:
                dm_type = dm.get('type')
                if dm_type == 1:
                    recipients = dm.get('recipients', [])
                    if recipients:
                        recipient = recipients[0]
                        display_name = recipient.get('global_name') or recipient.get('username', 'Unknown')
                        dms_list.append({
                            'id': dm['id'],
                            'display_name': display_name,
                            'type': 'dm'
                        })
                elif dm_type == 3:
                    name = dm.get('name') or 'Group DM'
                    dms_list.append({
                        'id': dm['id'],
                        'display_name': name,
                        'type': 'group_dm'
                    })
            
            # Load guilds from cache
            guilds_list = []
            cached_guilds = self.db.get_guilds()
            for guild in cached_guilds:
                guilds_list.append({
                    'id': guild['id'],
                    'name': guild['name'],
                    'type': 'guild'
                })
            
            # Update display
            if self.guilds_panel:
                self.guilds_panel.populate_from_data(dms_list, guilds_list)
            
            dm_count = len(dms_list)
            guild_count = len(guilds_list)
            
            if guild_count > 0 or dm_count > 0:
                self._update_status(f"[cyan]↻ Loaded {guild_count} guild(s) and {dm_count} DM(s) from cache[/cyan]")
        
        except Exception as e:
            logger.error(f"Error loading from cache: {e}", exc_info=e)
    
    async def connect_discord(self, token: str) -> None:
        """Connect to Discord and load guilds using aiohttp directly."""
        try:
            self._update_status("[yellow]Connecting to Discord...[/yellow]")
            
            import aiohttp
            
            headers = {
                "Authorization": token,
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36",
                "Accept": "*/*",
                "Accept-Encoding": "gzip, deflate, br",
                "Accept-Language": "en-US,en;q=0.9",
                "Origin": "https://discord.com",
                "Referer": "https://discord.com/channels/@me",
            }
            
            try:
                async with aiohttp.ClientSession(headers=headers) as session:
                    # Test token by getting current user
                    async with session.get("https://discord.com/api/v10/users/@me") as resp:
                        if resp.status == 401:
                            self._update_status("[red]✗ Invalid token (401)[/red]")
                            return
                        elif resp.status != 200:
                            self._update_status(f"[red]✗ Error: {resp.status}[/red]")
                            return
                        
                        user_data = await resp.json()
                        username = user_data.get('username', 'Unknown')
                        self._update_status(f"[green]✓ Logged in as {username}[/green]")
                        self.is_logged_in = True

                        # Start persistent gateway connection
                        self._update_status("[yellow]↻ Starting gateway connection...[/yellow]")
                        self.gateway = DiscordGateway(token)
                        # Start gateway in background
                        asyncio.create_task(self.gateway.connect())
                        self._update_status("[green]✓ Gateway connected[/green]")

                        # Get guilds
                        async with session.get("https://discord.com/api/v10/users/@me/guilds") as guilds_resp:
                            if guilds_resp.status == 200:
                                guilds_data = await guilds_resp.json()
                                await self._load_guilds_from_api(guilds_data, user_data, session)
                            else:
                                self._update_status(f"[red]✗ Failed to load guilds[/red]")
            
            except aiohttp.ClientError as e:
                self._update_status(f"[red]✗ Connection error[/red]")
            except Exception as e:
                self._update_status(f"[red]✗ Error[/red]")
        
        except Exception as e:
            self._update_status(f"[red]✗ Error[/red]")
    
    async def _load_guilds_from_api(self, guilds_data, user_data, session) -> None:
        """Load guilds from API response."""
        try:
            if not self.guilds_panel:
                return
            
            self._update_status("[yellow]Loading guilds and DMs...[/yellow]")
            
            dms_list = []
            guilds_list = []
            dms_data = []
            
            # Load DMs first
            async with session.get("https://discord.com/api/v10/users/@me/channels") as dms_resp:
                if dms_resp.status == 200:
                    dms_data = await dms_resp.json()
                    
                    for dm in sorted(dms_data, key=lambda d: d.get('last_message_id', '0'), reverse=True):
                        try:
                            dm_type = dm.get('type')
                            
                            if dm_type == 1:
                                recipient = dm.get('recipients', [{}])[0]
                                display_name = recipient.get('global_name') or recipient.get('username', 'Unknown')
                                dms_list.append({
                                    'id': dm['id'],
                                    'display_name': display_name,
                                    'username': recipient.get('username'),
                                    'type': 'dm'
                                })
                            elif dm_type == 3:
                                name = dm.get('name') or 'Group DM'
                                dms_list.append({
                                    'id': dm['id'],
                                    'display_name': name,
                                    'type': 'group_dm'
                                })
                        except Exception as e:
                            logger.error(f"Error loading DM: {e}")
            
            # Load guilds
            for guild in sorted(guilds_data, key=lambda g: g.get('name', '')):
                try:
                    guild_id = guild['id']
                    guild_name = guild['name']
                    
                    guilds_list.append({
                        'id': guild_id,
                        'name': guild_name,
                        'type': 'guild'
                    })
                
                except Exception as e:
                    logger.error(f"Error loading guild {guild.get('name')}: {e}")
            
            # Save to database
            self.db.save_guilds(guilds_data)
            self.db.save_dms(dms_data)
            
            # Update display
            if self.guilds_panel:
                self.guilds_panel.populate_from_data(dms_list, guilds_list)

            guild_count = len(guilds_data)
            dm_count = len(dms_list)
            self._update_status(f"[green]✓ Loaded {guild_count} guild(s) and {dm_count} DM(s)[/green]")

            # Lazy load all channels for all guilds in the background
            # This ensures channels are cached before user expands a guild
            logger.debug(f"Starting background channel loading for {len(guilds_list)} guilds...")
            asyncio.create_task(self._preload_all_guild_channels(guilds_list))
        
        except Exception as e:
            logger.error(f"Error loading guilds: {e}", exc_info=e)
            self._update_status(f"[red]✗ Error loading guilds[/red]")

    async def _preload_all_guild_channels(self, guilds_list: List[dict]) -> None:
        """Preload channels for all guilds in the background.

        This runs asynchronously so it doesn't block the UI. Channels are loaded
        with a small delay between requests to avoid rate limiting.
        """
        try:
            logger.debug(f"Starting preload of channels for {len(guilds_list)} guilds")
            for i, guild in enumerate(guilds_list):
                if i > 0:
                    # Add small delay between requests to avoid rate limiting
                    await asyncio.sleep(0.5)

                guild_id = guild.get('id')
                guild_name = guild.get('name', 'Unknown')

                # Check if channels are already cached
                cached_channels = self.db.get_channels(guild_id)
                if cached_channels:
                    logger.debug(f"Guild '{guild_name}' already has {len(cached_channels)} cached channels")
                    # Update the panel with cached channels
                    if self.guilds_panel:
                        self.guilds_panel.set_guild_channels(guild_id, cached_channels)
                    continue

                # Load channels from API for this guild
                logger.debug(f"Preloading channels for guild '{guild_name}'...")
                await self._load_guild_channels(guild)

            logger.debug("Finished preloading channels for all guilds")

        except Exception as e:
            logger.error(f"Error preloading guild channels: {e}", exc_info=e)

    async def _load_guild_channels(self, guild_data: dict) -> None:
        """Load channels for a guild when it's expanded."""
        try:
            guild_id = guild_data.get('id')
            if not guild_id:
                return

            import aiohttp
            import keyring
            from discordo.internal.consts import DISCORDO_NAME

            token = keyring.get_password(DISCORDO_NAME, 'token')
            if not token:
                return

            headers = {
                "Authorization": token,
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            }

            async with aiohttp.ClientSession(headers=headers) as session:
                url = f"https://discord.com/api/v10/guilds/{guild_id}/channels"
                async with session.get(url) as resp:
                    if resp.status == 200:
                        channels_raw = await resp.json()

                        # Format channels with full data
                        channels = []
                        for ch in channels_raw:
                            channels.append({
                                'id': ch.get('id'),
                                'name': ch.get('name', 'Unknown'),
                                'type': ch.get('type', 0),
                                'position': ch.get('position', 0),
                                'parent_id': ch.get('parent_id'),
                                'guild_id': guild_id,
                            })

                        # Cache channels
                        self.db.save_channels(guild_id, channels)

                        # Update guilds panel with channels
                        if self.guilds_panel:
                            self.guilds_panel.set_guild_channels(guild_id, channels)
                            self._update_status(f"[green]Loaded {len(channels)} channel(s)[/green]")
                    else:
                        self._update_status(f"[red]Failed to load channels: {resp.status}[/red]")

        except Exception as e:
            self._update_status(f"[red]Error loading channels[/red]")

    async def _load_channel_messages(self, channel_data: dict) -> None:
        """Load messages for a selected channel/DM."""
        try:
            channel_id = channel_data.get('id')
            if not channel_id:
                return
            
            import aiohttp
            import keyring
            from discordo.internal.consts import DISCORDO_NAME
            
            token = keyring.get_password(DISCORDO_NAME, 'token')
            if not token:
                self._update_status("[red]No token found[/red]")
                return
            
            headers = {
                "Authorization": token,
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            }
            
            async with aiohttp.ClientSession(headers=headers) as session:
                url = f"https://discord.com/api/v10/channels/{channel_id}/messages?limit=100"
                async with session.get(url) as resp:
                    if resp.status == 200:
                        messages_raw = await resp.json()

                        # Get guild roles and members from gateway cache (no API calls!)
                        guild_id = channel_data.get('guild_id')
                        guild_roles = self._get_guild_roles(guild_id) if guild_id else []
                        guild_members = self._get_guild_members(guild_id) if guild_id else {}

                        # Debug logging for member sync
                        if guild_id:
                            logger.info(f"Loading messages for guild {guild_id}")
                            logger.info(f"  Gateway ready: {self.gateway and self.gateway.state.ready}")
                            logger.info(f"  Guild roles cached: {len(guild_roles)} roles")
                            logger.info(f"  Guild members cached: {len(guild_members)} members")
                            if guild_roles:
                                logger.info(f"  Sample role: {guild_roles[0].get('name', 'unknown')} (color={guild_roles[0].get('color', 0)})")

                            # If members not cached but gateway exists, request them
                            if self.gateway and not guild_members:
                                logger.info(f"Members not cached, requesting from gateway...")
                                await self.gateway._request_guild_members(guild_id)
                                # Give members a moment to arrive before rendering (Discord usually responds within 100-200ms)
                                await asyncio.sleep(1.0)
                                # Re-fetch after request
                                guild_members = self._get_guild_members(guild_id)
                                logger.info(f"After request: {len(guild_members)} members cached")

                        # Format messages for display
                        messages = []
                        for msg in messages_raw:
                            full_timestamp = msg.get('timestamp', '')
                            time_str = ''
                            date_str = ''

                            if full_timestamp:
                                try:
                                    # ISO format: "2025-11-05T03:19:06.119000+00:00"
                                    if 'T' in full_timestamp:
                                        parts = full_timestamp.split('T')
                                        date_str = parts[0]  # "2025-11-05"
                                        time_part = parts[1].split('.')[0]  # "03:19:06"
                                        time_str = time_part
                                except Exception as e:
                                    logger.debug(f"Failed to parse timestamp {full_timestamp}: {e}")
                                    time_str = full_timestamp

                            author = msg.get('author', {})
                            author_color = '#5865F2'  # Discord default blue

                            # Get member color for guild messages (using cached data from gateway)
                            if guild_id and guild_roles and guild_members:
                                user_id = author.get('id')
                                if user_id and user_id in guild_members:
                                    member_data = guild_members[user_id]
                                    member_roles = member_data.get('roles', [])

                                    # Get highest role color using cached guild roles
                                    if member_roles:
                                        author_color = self._get_member_color(member_roles, guild_roles)
                                        logger.debug(f"Author {author.get('username', 'unknown')} color: {author_color}")
                                    else:
                                        logger.debug(f"Author {author.get('username', 'unknown')} has no roles")
                                else:
                                    logger.debug(f"Author {author.get('username', 'unknown')} not found in guild members")

                            messages.append({
                                'id': msg.get('id'),
                                'timestamp': time_str,  # Just the time HH:MM:SS
                                'date': date_str,  # The date YYYY-MM-DD
                                'full_timestamp': full_timestamp,  # Full ISO timestamp for reference
                                'author': author,
                                'author_color': author_color,
                                'content': msg.get('content', ''),
                                'embeds': msg.get('embeds', []),
                                'attachments': msg.get('attachments', []),
                                'reactions': msg.get('reactions', []),
                            })
                        
                        # Cache messages to database
                        channel_id = channel_data.get('id')
                        if channel_id and messages:
                            self.db.save_messages(channel_id, messages)

                        # Update messages panel
                        self.messages_panel = self.query_one("#messages-panel", MessagesPanel)
                        self.current_channel = channel_data
                        self.messages_panel.display_messages(messages, channel_data, app_ref=self)

                        self._update_status(f"[green]Loaded {len(messages)} message(s)[/green]")
                    else:
                        self._update_status(f"[red]Failed to load messages: {resp.status}[/red]")
        
        except Exception as e:
            self._update_status(f"[red]Error loading messages[/red]")

    async def _load_older_messages(self, channel_data: dict, before_message_id: str) -> None:
        """Load older messages before a specific message ID (for lazy loading)."""
        try:
            channel_id = channel_data.get('id')
            if not channel_id:
                return

            import aiohttp
            import keyring
            from discordo.internal.consts import DISCORDO_NAME

            token = keyring.get_password(DISCORDO_NAME, 'token')
            if not token:
                return

            headers = {
                "Authorization": token,
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            }

            async with aiohttp.ClientSession(headers=headers) as session:
                # Load messages before the oldest message ID (100 per batch for aggressive loading)
                url = f"https://discord.com/api/v10/channels/{channel_id}/messages?limit=100&before={before_message_id}"

                # Add timeout to prevent indefinite hangs
                timeout = aiohttp.ClientTimeout(total=15)
                async with session.get(url, timeout=timeout) as resp:
                    if resp.status == 200:
                        messages_raw = await resp.json()

                        if not messages_raw:
                            # No more messages to load
                            if self.messages_panel:
                                self.messages_panel.has_more_messages = False
                                self.messages_panel.is_loading = False
                            return

                        # Get guild roles and members from gateway cache (no API calls!)
                        guild_id = channel_data.get('guild_id')
                        guild_roles = self._get_guild_roles(guild_id) if guild_id else []
                        guild_members = self._get_guild_members(guild_id) if guild_id else {}
                    elif resp.status == 401:
                        logger.error("Authentication failed - token may be expired")
                        if self.messages_panel:
                            self.messages_panel.is_loading = False
                        self._update_status("[red]Auth failed - token expired?[/red]")
                        return
                    elif resp.status == 429:
                        logger.warning("Rate limited by Discord - waiting...")
                        if self.messages_panel:
                            self.messages_panel.is_loading = False
                        self._update_status("[yellow]Rate limited - wait before scrolling again[/yellow]")
                        return
                    else:
                        logger.error(f"Discord API error {resp.status} loading older messages from {channel_id}")
                        if self.messages_panel:
                            self.messages_panel.is_loading = False
                        self._update_status(f"[red]API error {resp.status}[/red]")
                        return

                    # Only reach here if resp.status == 200 (successful)
                    # Format messages for display (same as _load_channel_messages)
                    messages = []
                    for msg in messages_raw:
                        full_timestamp = msg.get('timestamp', '')
                        time_str = ''
                        date_str = ''

                        if full_timestamp:
                            try:
                                # ISO format: "2025-11-05T03:19:06.119000+00:00"
                                if 'T' in full_timestamp:
                                    parts = full_timestamp.split('T')
                                    date_str = parts[0]  # "2025-11-05"
                                    time_part = parts[1].split('.')[0]  # "03:19:06"
                                    time_str = time_part
                            except Exception as e:
                                logger.debug(f"Failed to parse timestamp {full_timestamp}: {e}")
                                time_str = full_timestamp

                        author = msg.get('author', {})
                        author_color = '#5865F2'

                        # Get member color for guild messages (using cached data from gateway)
                        if guild_id and guild_roles and guild_members:
                            user_id = author.get('id')
                            if user_id and user_id in guild_members:
                                member_data = guild_members[user_id]
                                member_roles = member_data.get('roles', [])

                                # Get highest role color using cached guild roles
                                if member_roles:
                                    author_color = self._get_member_color(member_roles, guild_roles)

                        messages.append({
                            'id': msg.get('id'),
                            'timestamp': time_str,  # Just the time HH:MM:SS
                            'date': date_str,  # The date YYYY-MM-DD
                            'full_timestamp': full_timestamp,  # Full ISO timestamp for reference
                            'author': author,
                            'author_color': author_color,
                            'content': msg.get('content', ''),
                            'embeds': msg.get('embeds', []),
                            'attachments': msg.get('attachments', []),
                            'reactions': msg.get('reactions', []),
                        })

                    # Cache these older messages (outside the for loop)
                    channel_id = channel_data.get('id')
                    if channel_id and messages:
                        self.db.save_messages(channel_id, messages)

                    # Update messages panel - prepend these older messages
                    if self.messages_panel:
                        self.messages_panel.display_messages(messages, channel_data, prepend=True)
                        self.messages_panel.is_loading = False
                        self._update_status(f"[green]Loaded {len(messages)} older message(s)[/green]")

        except Exception as e:
            logger.error(f"Error loading older messages: {type(e).__name__}: {e}", exc_info=True)
            if self.messages_panel:
                self.messages_panel.is_loading = False
            self._update_status(f"[red]Error loading messages: {type(e).__name__}[/red]")

    async def _send_message(self, content: str) -> None:
        """Send a message to the current channel."""
        logger.info(f"_send_message called with content length: {len(content)}")

        if not self.current_channel:
            logger.warning("No current channel selected")
            self._update_status("[red]No channel selected[/red]")
            return

        channel_id = self.current_channel.get('id')
        if not channel_id:
            logger.warning("Current channel has no ID")
            self._update_status("[red]Invalid channel[/red]")
            return

        logger.info(f"Sending message to channel: {channel_id}")

        try:
            logger.debug("Importing keyring and DISCORDO_NAME constant")
            import keyring
            from discordo.internal.consts import DISCORDO_NAME

            logger.debug(f"Getting token from keyring for {DISCORDO_NAME}")
            token = keyring.get_password(DISCORDO_NAME, 'token')
            if not token:
                logger.warning("Token not found in keyring")
                self._update_status("[red]Token not found - please login again[/red]")
                return

            logger.debug("Creating headers with token")
            headers = {
                "Authorization": token,
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            }

            # Create message payload
            logger.debug(f"Creating message payload: {len(content)} chars")
            payload = {"content": content}

            logger.debug("Creating aiohttp ClientSession")
            async with aiohttp.ClientSession(headers=headers) as session:
                url = f"https://discord.com/api/v10/channels/{channel_id}/messages"
                timeout = aiohttp.ClientTimeout(total=15)

                logger.info(f"Sending POST request to: {url}")
                try:
                    async with session.post(url, json=payload, timeout=timeout) as resp:
                        logger.info(f"API response status: {resp.status}")
                        if resp.status == 200:
                            # Message sent successfully
                            logger.info("Message sent successfully, parsing response")
                            message_data = await resp.json()
                            logger.debug(f"Message data: id={message_data.get('id')}, author={message_data.get('author', {}).get('username')}")
                            self._update_status("[green]Message sent[/green]")

                            # Add the sent message to the display
                            logger.debug("Adding sent message to display")
                            if self.messages_panel:
                                # Create message dict in same format as loaded messages
                                author = message_data.get('author', {})
                                full_timestamp = message_data.get('timestamp', '')
                                time_str = ''
                                date_str = ''

                                if full_timestamp:
                                    try:
                                        if 'T' in full_timestamp:
                                            parts = full_timestamp.split('T')
                                            date_str = parts[0]
                                            time_part = parts[1].split('.')[0]
                                            time_str = time_part
                                    except Exception as e:
                                        logger.debug(f"Failed to parse timestamp {full_timestamp}: {e}")
                                        time_str = full_timestamp

                                # Get member color if in a guild
                                author_color = '#5865F2'
                                guild_id = self.current_channel.get('guild_id')
                                if guild_id:
                                    guild_roles = self._get_guild_roles(guild_id)
                                    guild_members = self._get_guild_members(guild_id)
                                    user_id = author.get('id')

                                    if user_id and guild_members and user_id in guild_members:
                                        member_data = guild_members[user_id]
                                        member_roles = member_data.get('roles', [])
                                        if member_roles and guild_roles:
                                            author_color = self._get_member_color(member_roles, guild_roles)

                                sent_message = {
                                    'id': message_data.get('id'),
                                    'timestamp': time_str,
                                    'date': date_str,
                                    'full_timestamp': full_timestamp,
                                    'author': author,
                                    'author_color': author_color,
                                    'content': message_data.get('content', ''),
                                    'embeds': message_data.get('embeds', []),
                                    'attachments': message_data.get('attachments', []),
                                    'reactions': message_data.get('reactions', []),
                                }

                                # Append sent message to the bottom (not clearing history)
                                if self.messages_panel and self.messages_panel.messages_list:
                                    # Add to messages data
                                    self.messages_panel.messages_data.append(sent_message)
                                    logger.debug(f"Added message to messages_data, now {len(self.messages_panel.messages_data)} messages")

                                    # Create widget for the message (not grouped - new message from user)
                                    container_width = self.messages_panel._update_container_width()
                                    message_widget = MessageItemWidget(sent_message, container_width, is_grouped=False)

                                    # Append to list view
                                    self.messages_panel.messages_list.append(ListItem(message_widget))
                                    logger.debug("Message widget appended to messages_list")

                                    # Scroll to bottom to show the new message
                                    try:
                                        last_index = len(self.messages_panel.messages_list) - 1
                                        self.messages_panel.messages_list.index = last_index
                                        self.messages_panel.messages_list.scroll_visible(animate=False)
                                        logger.debug(f"Scrolled to bottom (index {last_index})")
                                    except Exception as scroll_err:
                                        logger.warning(f"Failed to scroll to bottom: {scroll_err}")

                        elif resp.status == 401:
                            logger.error("Authentication failed - token expired or invalid")
                            self._update_status("[red]Auth failed - token expired?[/red]")
                        elif resp.status == 429:
                            logger.warning("Rate limited by Discord API")
                            self._update_status("[yellow]Rate limited - wait before sending again[/yellow]")
                        elif resp.status == 403:
                            logger.error(f"Permission denied sending message to {channel_id}")
                            self._update_status("[red]Permission denied - cannot send to this channel[/red]")
                        else:
                            error_text = ""
                            try:
                                error_data = await resp.json()
                                logger.error(f"Discord API error {resp.status}: {error_data}")
                                if 'message' in error_data:
                                    error_text = error_data['message']
                            except:
                                error_text = await resp.text()
                                logger.error(f"Discord API error {resp.status}: {error_text}")

                            self._update_status(f"[red]Failed to send message: {resp.status}[/red]")

                except asyncio.TimeoutError:
                    self._update_status("[red]Message send timeout[/red]")
                except Exception as e:
                    logger.error(f"Error sending message: {type(e).__name__}: {e}")
                    self._update_status(f"[red]Error sending message: {type(e).__name__}[/red]")

        except Exception as e:
            logger.error(f"Error preparing message: {type(e).__name__}: {e}", exc_info=True)

            # Tell user where to find logs
            from discordo.internal.logger import default_path
            log_path = default_path()
            logger.error(f"See full error details in: {log_path}")

            self._update_status(f"[red]Error preparing message - check logs at ~/.cache/discordo/logs.txt[/red]")

    def action_move_up(self) -> None:
        """Move selection up."""
        if self.guilds_panel:
            self.guilds_panel.action_cursor_up()
    
    def action_move_down(self) -> None:
        """Move selection down."""
        if self.guilds_panel:
            self.guilds_panel.action_cursor_down()
    
    def action_select_item(self) -> None:
        """Select current item or toggle folder."""
        if self.guilds_panel:
            if hasattr(self.guilds_panel, 'highlighted_index'):
                idx = self.guilds_panel.highlighted_index
            elif hasattr(self.guilds_panel, '_selected_index'):
                idx = self.guilds_panel._selected_index
            else:
                return
            
            if idx is not None and idx < len(self.guilds_panel.all_items):
                item_type, item_data = self.guilds_panel.all_items[idx]
                
                if item_type == 'folder':
                    folder_id = item_data['id']
                    self.guilds_panel.folders_open[folder_id] = not self.guilds_panel.folders_open[folder_id]
                    self.guilds_panel.rebuild_list()
                else:
                    self.guilds_panel.post_message(CollapsibleOptionList.ItemSelected(item_type, item_data))
    
    def action_toggle_favorite(self) -> None:
        """Toggle favorite for the currently active guild/DM item."""
        # Only allow favoriting guilds and DMs, not channels or folders
        if not self.active_guild_item:
            return

        item_type, item_data = self.active_guild_item
        if item_type not in ('guild', 'dm'):
            return

        item_id = item_data.get('id')
        item_name = item_data.get('name') or item_data.get('display_name', 'Unknown')

        if not item_id or not self.guilds_panel:
            return

        # Toggle favorite in memory
        if item_id in self.guilds_panel.favorites:
            self.guilds_panel.favorites.discard(item_id)
            # Remove from database
            if self.db:
                self.db.remove_favorite(item_id)
            logger.debug(f"Removed {item_type} '{item_name}' from favorites")
        else:
            self.guilds_panel.favorites.add(item_id)
            # Add to database
            if self.db:
                self.db.add_favorite(item_id, item_type, item_name)
            logger.debug(f"Added {item_type} '{item_name}' to favorites")

        # Rebuild list to show star
        self.guilds_panel.preserve_cursor_item = (item_type, item_data)
        self.guilds_panel.rebuild_list()
    
    def _update_status(self, message: str) -> None:
        """Update status bar."""
        try:
            if self.status_panel:
                self.status_panel.update_status(message)
        except Exception as e:
            logger.debug(f"Could not update status: {e}")

    def _get_guild_roles(self, guild_id: str) -> List[dict]:
        """Get guild roles from gateway cache (no API call)."""
        if self.gateway:
            return self.gateway.state.get_guild_roles(guild_id)
        return []

    def _get_guild_members(self, guild_id: str) -> dict:
        """Get guild members from gateway cache (no API call)."""
        if self.gateway:
            return self.gateway.state.get_guild_members(guild_id)
        return {}

    def _get_member_color(self, member_roles: List[str], guild_roles: List[dict]) -> str:
        """Get the highest role color for a member. Returns hex color string."""
        # member_roles is a list of role IDs
        # guild_roles is sorted by position (highest first)
        # Return the first role that has a color

        for guild_role in guild_roles:
            role_id = guild_role.get('id')
            if role_id in member_roles:
                color = guild_role.get('color', 0)
                if color != 0:  # Only return non-zero colors
                    return f"#{color:06x}"

        # Default Discord blue
        return '#5865F2'

    def action_quit(self) -> None:
        """Quit the app."""
        try:
            # Close gateway connection
            if self.gateway:
                asyncio.create_task(self.gateway.close())
        except Exception as e:
            logger.debug(f"Error closing gateway: {e}")

        try:
            if hasattr(self, 'db'):
                self.db.close()
        except Exception as e:
            logger.debug(f"Error closing database: {e}")

        self.exit()
    
    def action_logout(self) -> None:
        """Logout and clear token."""
        import keyring
        from discordo.internal.consts import DISCORDO_NAME
        
        try:
            keyring.delete_password(DISCORDO_NAME, 'token')
            self._update_status("[yellow]Token cleared[/yellow]")
        except Exception as e:
            logger.error(f"Could not clear token: {e}")
        
        self.exit()


def run_app(cfg: Config) -> None:
    """Run the Discordo application."""
    import sys
    
    # Set up logging to capture to buffer
    log_handler = logging.StreamHandler(_log_buffer)
    log_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    # Disable all logging output to terminal
    logging.getLogger().setLevel(logging.CRITICAL + 1)  # Effectively disables all logging
    logging.getLogger().addHandler(log_handler)
    
    app = DiscordoApp(cfg)
    try:
        app.run()
    finally:
        # Print all captured logs when app exits
        log_content = _log_buffer.getvalue()
        if log_content:
            print("\n" + "="*80)
            print("APPLICATION LOGS")
            print("="*80)
            print(log_content)
            print("="*80)

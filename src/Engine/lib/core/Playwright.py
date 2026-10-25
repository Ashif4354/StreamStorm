from os.path import join
from asyncio import Lock, create_task
from logging import getLogger, Logger
from playwright.async_api import (
    async_playwright,
    Playwright as AsyncPlaywright,
    TimeoutError as PlaywrightTimeoutError,
)
from playwright.async_api._generated import Browser, BrowserContext, Locator, Page

from .BrowserAutomator import BrowserAutomator
from ..utils.exceptions import BrowserClosedError, ElementNotFound
from ..settings import settings 

logger: Logger = getLogger(f"streamstorm.{__name__}")

_OBSCURA_HYDRATION_SCRIPT: str = """
async () => {
    // 1. Patch document.evaluate so Playwright XPath locators work reliably in Obscura
    if (!document.__obscuraXPathPatched) {
        document.__obscuraXPathPatched = true;
        const nativeEval = document.evaluate ? document.evaluate.bind(document) : null;

        function makeXPathResult(nodes) {
            let idx = 0;
            return {
                resultType: 7,
                singleNodeValue: nodes[0] || null,
                snapshotLength: nodes.length,
                snapshotItem(i) { return nodes[i] || null; },
                iterateNext() { return idx < nodes.length ? nodes[idx++] : null; },
                invalidIteratorState: false
            };
        }

        function normText(s) {
            return (s || '').replace(/\\s+/g, ' ').trim();
        }

        document.evaluate = function(expression, contextNode, resolver, type, result) {
            const root = (contextNode && contextNode.querySelectorAll) ? contextNode : document;
            const expr = (expression || '').trim();

            if (expr === '//*[@id="avatar-btn"]') {
                const el = document.getElementById('avatar-btn');
                return makeXPathResult(el ? [el] : []);
            }
            if (expr === "//*[text()='Switch account']") {
                const sw = document.getElementById('obscura-switch-account');
                if (sw) return makeXPathResult([sw]);
                const matches = Array.from(root.querySelectorAll('*')).filter(
                    el => el.children.length === 0 && el.textContent === 'Switch account'
                );
                return makeXPathResult(matches);
            }
            const nameMatch = expr.match(/^\\/\\/\\*\\[@id='contents'\\]\\/ytd-account-item-renderer\\[\\.\\/\\/text\\(\\)\\[normalize-space\\(\\.\\)='(.+)'\\]\\]$/);
            if (nameMatch) {
                const targetName = nameMatch[1];
                const items = Array.from(document.querySelectorAll('#contents ytd-account-item-renderer')).filter(
                    el => normText(el.getAttribute('data-channel-name') || el.textContent) === normText(targetName)
                );
                return makeXPathResult(items);
            }
            const idxMatch = expr.match(/^\\/\\/\\*\\[@id='contents'\\]\\/ytd-account-item-renderer\\[(\\d+)\\]$/);
            if (idxMatch) {
                const idx = parseInt(idxMatch[1], 10) - 1;
                const items = Array.from(document.querySelectorAll('#contents ytd-account-item-renderer'));
                return makeXPathResult(items[idx] ? [items[idx]] : []);
            }
            if (expr === '//*[@id="confirm-button"]//button') {
                return makeXPathResult(Array.from(document.querySelectorAll('#confirm-button button')));
            }
            if (expr === "//button[.//div[text()='Subscribe']]") {
                const btns = Array.from(root.querySelectorAll('button')).filter(
                    b => Array.from(b.querySelectorAll('div')).some(d => d.textContent.trim() === 'Subscribe')
                );
                return makeXPathResult(btns);
            }
            if (expr === "//button[.//span[text()='Subscribe']]") {
                const btns = Array.from(root.querySelectorAll('button')).filter(
                    b => Array.from(b.querySelectorAll('span')).some(s => s.textContent.trim() === 'Subscribe')
                );
                return makeXPathResult(btns);
            }
            if (expr === "//yt-live-chat-text-input-field-renderer//div[@id='input']") {
                const inp = Array.from(document.querySelectorAll('yt-live-chat-text-input-field-renderer #input'));
                return makeXPathResult(inp);
            }

            if (nativeEval) {
                try {
                    return nativeEval(expression, contextNode, resolver, type, result);
                } catch (e) {}
            }
            return makeXPathResult([]);
        };
    }

    // 2. Helper for authenticated InnerTube API calls inside Obscura
    if (!window.__obscuraYtFetch) {
        window.__obscuraYtFetch = async function(apiPath, payload) {
            function getCookie(name) {
                const m = document.cookie.match(new RegExp('(?:^|; )' + name.replace(/([.$?*|{}()\\[\\]\\\\/+^])/g, '\\\\$1') + '=([^;]*)'));
                return m ? decodeURIComponent(m[1]) : null;
            }
            async function sha1(str) {
                const buf = new TextEncoder().encode(str);
                const hash = await crypto.subtle.digest('SHA-1', buf);
                return Array.from(new Uint8Array(hash)).map(b => b.toString(16).padStart(2, '0')).join('');
            }
            const sapisid = getCookie('SAPISID') || getCookie('__Secure-3PAPISID') || '';
            const ts = Math.floor(Date.now() / 1000);
            const origin = 'https://www.youtube.com';
            const hashVal = await sha1(`${ts} ${sapisid} ${origin}`);
            const ytcfg = window.ytcfg;
            const context = ytcfg ? ytcfg.get('INNERTUBE_CONTEXT') : {};
            const apiKey = ytcfg ? ytcfg.get('INNERTUBE_API_KEY') : '';

            const headers = {
                'Content-Type': 'application/json',
                'Authorization': `SAPISIDHASH ${ts}_${hashVal} SAPISID1PHASH ${ts}_${hashVal} SAPISID3PHASH ${ts}_${hashVal}`,
                'X-Origin': origin,
                'X-Youtube-Client-Name': String((ytcfg && ytcfg.get('INNERTUBE_CONTEXT_CLIENT_NAME')) || '1'),
                'X-Youtube-Client-Version': (ytcfg && ytcfg.get('INNERTUBE_CONTEXT_CLIENT_VERSION')) || '',
                'X-Goog-AuthUser': String((ytcfg && ytcfg.get('SESSION_INDEX')) || '0'),
                'X-Youtube-Bootstrap-Logged-In': 'true',
            };
            const delegatedId = ytcfg && ytcfg.get('DELEGATED_SESSION_ID');
            if (delegatedId) {
                headers['X-Goog-PageId'] = String(delegatedId);
            }
            const visitorData = ytcfg && ytcfg.get('VISITOR_DATA');
            if (visitorData) {
                headers['X-Goog-Visitor-Id'] = String(visitorData);
            }

            const resp = await fetch(`${apiPath}?key=${apiKey}&prettyPrint=false`, {
                method: 'POST',
                credentials: 'include',
                headers,
                body: JSON.stringify(Object.assign({ context }, payload))
            });
            return { status: resp.status, ok: resp.ok, data: await resp.json().catch(() => ({})) };
        };
    }

    function findAllByKey(obj, targetKey, results = []) {
        if (!obj || typeof obj !== 'object') return results;
        if (targetKey in obj) results.push(obj[targetKey]);
        for (const k of Object.keys(obj)) {
            findAllByKey(obj[k], targetKey, results);
        }
        return results;
    }

    if (!location.hostname.includes('youtube.com')) {
        return { hydrated: false, reason: 'non-youtube' };
    }

    const ytData = window.ytInitialData;
    const loggedOut = ytData?.responseContext?.mainAppWebResponseContext?.loggedOut;

    let container = document.getElementById('obscura-yt-hydration');
    if (container) container.remove();
    container = document.createElement('div');
    container.id = 'obscura-yt-hydration';
    container.style.cssText = 'display:block;padding:16px;background:#0f0f0f;color:#fff;font-family:sans-serif;z-index:999999;position:relative;';
    document.body.insertBefore(container, document.body.firstChild);

    // 3. Hydrate Account & Channel Switcher UI on /account
    if (location.pathname.startsWith('/account') && loggedOut === false) {
        const avatarBtn = document.createElement('button');
        avatarBtn.id = 'avatar-btn';
        avatarBtn.style.cssText = 'display:inline-block;padding:8px 16px;margin:4px;cursor:pointer;';
        avatarBtn.textContent = 'Account';
        container.appendChild(avatarBtn);

        const switchBtn = document.createElement('div');
        switchBtn.id = 'obscura-switch-account';
        switchBtn.style.cssText = 'display:block;padding:8px 16px;margin:4px;cursor:pointer;';
        switchBtn.textContent = 'Switch account';
        container.appendChild(switchBtn);

        const contentsDiv = document.createElement('div');
        contentsDiv.id = 'contents';
        contentsDiv.style.cssText = 'display:block;padding:8px;';
        container.appendChild(contentsDiv);

        try {
            const resp = await fetch('https://www.youtube.com/getAccountSwitcherEndpoint', { credentials: 'include' });
            let text = await resp.text();
            if (text.startsWith(")]}'")) {
                text = text.split('\\n').slice(1).join('\\n');
            }
            const switcherData = JSON.parse(text);
            const accountItems = findAllByKey(switcherData, 'accountItem');

            for (const item of accountItems) {
                const chName = item?.accountName?.simpleText || item?.accountName?.runs?.[0]?.text || '';
                if (!chName) continue;
                const isSelected = Boolean(item?.isSelected);
                const tokens = item?.serviceEndpoint?.selectActiveIdentityEndpoint?.supportedTokens || [];
                let signinUrl = '';
                let pageId = '';
                for (const t of tokens) {
                    if (t?.accountSigninToken?.signinUrl) {
                        signinUrl = t.accountSigninToken.signinUrl;
                    }
                    if (t?.pageIdToken?.pageId) {
                        pageId = t.pageIdToken.pageId;
                    }
                }
                if (!signinUrl && pageId) {
                    signinUrl = `/signin?action_handle_signin=true&authuser=0&pageid=${pageId}&next=%2Faccount&feature=masthead_switcher&skip_identity_prompt=true`;
                }
                if (signinUrl) {
                    signinUrl = signinUrl.replace('next=%2F&', 'next=%2Faccount&');
                }

                const renderer = document.createElement('ytd-account-item-renderer');
                renderer.style.cssText = 'display:block;padding:8px;margin:4px 0;border:1px solid #333;cursor:pointer;';
                renderer.setAttribute('data-channel-name', chName);
                renderer.setAttribute('data-is-selected', String(isSelected));
                if (signinUrl) {
                    renderer.setAttribute('data-signin-url', signinUrl);
                }
                const span = document.createElement('span');
                span.id = 'channel-title';
                span.textContent = chName;
                renderer.appendChild(span);
                contentsDiv.appendChild(renderer);
            }
        } catch (err) {
            console.error('Obscura account switcher hydration error:', err);
        }
        return { hydrated: true, page: 'account' };
    }

    // 4. Hydrate Live Chat Input & Message Sender on /live_chat
    if (location.pathname.startsWith('/live_chat')) {
        const sendEndpoints = findAllByKey(ytData, 'sendLiveChatMessageEndpoint');
        if (sendEndpoints.length > 0) {
            const sendEp = sendEndpoints[0];
            window.__obscuraChatMsgCounter = window.__obscuraChatMsgCounter || 0;

            const chatRenderer = document.createElement('yt-live-chat-text-input-field-renderer');
            chatRenderer.style.cssText = 'display:block;padding:12px;';

            const inputEl = document.createElement('input');
            inputEl.id = 'input';
            inputEl.type = 'text';
            inputEl.placeholder = 'Chat...';
            inputEl.style.cssText = 'display:block;width:320px;height:36px;padding:4px 8px;';

            inputEl.addEventListener('keydown', (e) => {
                if (e.key === 'Enter') {
                    const msg = inputEl.value || '';
                    inputEl.value = '';
                    if (!msg) return;
                    const msgId = (sendEp.clientIdPrefix || 'obscura_msg_') + String(window.__obscuraChatMsgCounter++);
                    window.__obscuraLastSendPromise = window.__obscuraYtFetch('/youtubei/v1/live_chat/send_message', {
                        params: sendEp.params,
                        clientMessageId: msgId,
                        richMessage: {
                            textSegments: [{ text: msg }]
                        }
                    });
                }
            });

            chatRenderer.appendChild(inputEl);
            container.appendChild(chatRenderer);
            return { hydrated: true, page: 'live_chat' };
        }
        return { hydrated: false, page: 'live_chat_no_endpoint' };
    }

    // 5. Hydrate Subscribe Button on Channel / Video pages
    const subEndpoints = findAllByKey(ytData, 'subscribeEndpoint');
    if (subEndpoints.length > 0) {
        const subRenderers = findAllByKey(ytData, 'subscribeButtonRenderer');
        const alreadySubscribed = subRenderers.some(r => r && r.subscribed === true);
        if (!alreadySubscribed) {
            const ep = subEndpoints[0];
            const subBtn = document.createElement('button');
            subBtn.id = 'obscura-subscribe-btn';
            subBtn.style.cssText = 'display:inline-block;padding:8px 16px;margin:8px;cursor:pointer;';

            const divTxt = document.createElement('div');
            divTxt.textContent = 'Subscribe';
            const spanTxt = document.createElement('span');
            spanTxt.textContent = 'Subscribe';
            subBtn.appendChild(divTxt);
            subBtn.appendChild(spanTxt);

            subBtn.addEventListener('click', () => {
                window.__obscuraLastActionPromise = window.__obscuraYtFetch('/youtubei/v1/subscription/subscribe', {
                    channelIds: ep.channelIds || [],
                    params: ep.params || ''
                });
            });
            container.appendChild(subBtn);
            return { hydrated: true, page: 'subscribe' };
        }
    }

    return { hydrated: true, page: 'other' };
}
"""

class Playwright(BrowserAutomator):
    __slots__: tuple[str, ...] = (
        'user_data_dir', 'background', '_is_alive', 'cookies',
        'playwright', 'browser_context', 'browser', 'page', 'index', 'channel_name',
        '_is_obscura'
    )
    
    _chrome_version: str = None
    _version_lock: Lock = Lock()

    _shared_playwright: AsyncPlaywright | None = None
    _shared_playwright_refcount: int = 0
    _playwright_lock: Lock = Lock()

    def __init__(self, user_data_dir: str, background: bool, cookies: list[dict] | None = None, index: int = 0, channel_name: str = "") -> None:
        self.user_data_dir: str = user_data_dir
        self.background: bool = background
        self.cookies: list[dict] | None = cookies or []
        self._is_alive: bool = True
        self.index: int = index
        self.channel_name: str = channel_name
        self._is_obscura: bool = False
        
    async def __get_chromium_options(self) -> dict[str, str | bool | list[str]]:
        options: dict[str, str | bool | list[str]] = {
            "headless": self.background,
            "args": [
                "--autoplay-policy=user-gesture-required",
                "--blink-settings=imagesEnabled=false",
                "--disable-animations",
                "--disable-default-apps",
                "--disable-dev-shm-usage",
                "--disable-extensions",
                "--disable-logging",
                "--disable-notifications",
                "--enable-low-end-device-mode",
                "--hide-scrollbars",
                "--metrics-recording-only",
                "--mute-audio",
                "--no-sandbox",
                "--password-store=basic",
            ],
            "viewport": {"width": 1200, "height": 800},
            "channel": "chrome"
        }

        if settings.login_method == "profiles":
            options["user_data_dir"] = self.user_data_dir
        
        if self.background:
            options["args"].extend([
                "--disable-software-rasterizer",
                "--enable-unsafe-swiftshader",
                "--use-angle=swiftshader",
                "--use-gl=angle"
            ])

        return options

    async def __close_about_blank_page(self) -> None:
        """Close the about:blank page if it exists."""
        try:
            for page in self.browser_context.pages:
                if page.url == "about:blank":
                    await page.close()
                    break
        except Exception as e:
            logger.error(f"[{self.index}] [{self.channel_name}] : Error closing about:blank page: {e}")

    @classmethod
    async def __get_browser_version(cls, playwright: AsyncPlaywright, is_obscura: bool = False) -> str:
        if is_obscura:
            return cls._chrome_version or "131.0.0.0"

        if cls._chrome_version is None:
            async with cls._version_lock:
                if cls._chrome_version is None: # We are checking two times because multiple coroutines could be trying to access this at the same time
                    try:
                        browser_obj: Browser = await playwright.chromium.launch(channel="chrome")
                        cls._chrome_version = browser_obj.version
                        await browser_obj.close()
                    except Exception:
                        cls._chrome_version = "131.0.0.0"
                    
        return cls._chrome_version
    
    def _attach_error_listeners(self):
        def mark_dead(marker: str):
            self._is_alive = False
            logger.debug(f"[{self.index}] [{self.channel_name}] : ##### StreamStorm instance marked as dead by: {marker}")

        try:
            self.page.on("close", lambda _: mark_dead("page.on_close"))
            self.page.on("crash", lambda _: mark_dead("page.on_crash"))
            self.browser_context.on("close", lambda _: mark_dead("browser_context.on_close"))
            self.browser_context.browser.on("disconnected", lambda _: mark_dead("browser_context.browser.on_disconnected"))

        except Exception as _:
            self._is_alive = False
            logger.debug(f"[{self.index}] [{self.channel_name}] : ##### StreamStorm instance marked as dead by: Failure to attach error listeners")
            
    async def check_language_english(self) -> bool:
        language: str = await self.page.evaluate("navigator.language")        
        
        return language.startswith("en")
        
    def change_language(self):
        raise NotImplementedError    

    async def _hydrate_obscura_page(self) -> None:
        """Hydrate YouTube SPA state into interactive DOM elements when running in Obscura."""
        if not self._is_obscura:
            return
        try:
            res = await self.page.evaluate(_OBSCURA_HYDRATION_SCRIPT)
            logger.debug(f"[{self.index}] [{self.channel_name}] Obscura hydration result: {res}")
        except Exception as e:
            logger.debug(f"[{self.index}] [{self.channel_name}] Obscura hydration skipped/error: {e}")

    async def open_browser(self, obscura_port: int | None = None) -> None:
        async with Playwright._playwright_lock:
            if Playwright._shared_playwright is None:
                Playwright._shared_playwright = await async_playwright().start()
            Playwright._shared_playwright_refcount += 1
            self.playwright = Playwright._shared_playwright

        self._is_obscura = bool(obscura_port and settings.engine == "obscura")

        browser_options: dict[str, str | bool | list[str]] = await self.__get_chromium_options()
        logger.debug(f"[{self.index}] [{self.channel_name}] Browser options configured with {len(browser_options['args'])} arguments")
        logger.debug(f"[{self.index}] [{self.channel_name}] Browser arguments: {'\n'.join(browser_options['args'])}")
        
        if settings.login_method == "profiles":        
            self.browser_context: BrowserContext = (
                await self.playwright.chromium.launch_persistent_context(
                    **browser_options
                )
            )

        elif settings.login_method == "cookies":
            view_port: dict = browser_options.pop("viewport")

            if self._is_obscura:
                self.browser: Browser = await self.playwright.chromium.connect_over_cdp(f"http://127.0.0.1:{obscura_port}")
            else: 
                self.browser: Browser = await self.playwright.chromium.launch(**browser_options)

            self.browser_context: BrowserContext = await self.browser.new_context(
                viewport=view_port
            )            
            
            if self._is_obscura:
                cookies_to_add: list[dict] = [
                        {**c, "domain": c["domain"].lstrip(".")} if c.get("domain", "").startswith(".") else c
                        for c in self.cookies
                    ]
                
                await self.browser_context.add_cookies(cookies_to_add)
            
            else:
                await self.browser_context.add_cookies(self.cookies)

        else:
            raise SystemError("Invalid login method")

        self.page: Page = await self.browser_context.new_page()
        
        if settings.login_method == "profiles":
            create_task(self.__close_about_blank_page())

        self.page.set_default_navigation_timeout(45000)
        self.page.set_default_timeout(45000)
        
        browser_version: str = await self.__get_browser_version(self.playwright, is_obscura=self._is_obscura)
        logger.debug(f"[{self.index}] [{self.channel_name}] Browser version: {browser_version}")
        
        await self.page.set_extra_http_headers({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                          f"(KHTML, like Gecko) Chrome/{browser_version} Safari/537.36"
        })

        self._attach_error_listeners()
        logger.debug(f"[{self.index}] [{self.channel_name}] Browser setup completed")
        
    async def capture_screenshot(self, name: str) -> None:
        try:
            settings.screenshot_dir.mkdir(parents=True, exist_ok=True)
            path: str = join(settings.screenshot_dir, f"[{self.index}]-[{self.channel_name}]-{name}.png")
            await self.page.screenshot(path=path)
            logger.debug(f"[{self.index}] [{self.channel_name}] Screenshot captured: {path}")
        except Exception as e:
            logger.debug(f"[{self.index}] [{self.channel_name}] Screenshot skipped ({name}): {e}")
            
 
    async def go_to_page(self, url: str) -> None:
        
        try:
            await self.page.goto(url)
            if self._is_obscura:
                await self._hydrate_obscura_page()
            logger.info(f"[{self.index}] [{self.channel_name}] Successfully navigated to: {url}")
            
        except PlaywrightTimeoutError as e:
            logger.error(f"[{self.index}] [{self.channel_name}] : Timeout error occurred while navigating to {url}: {e}")
            await self.close_browser(reason="Timeout while navigating to page")
            raise BrowserClosedError from e

    async def find_element(self, selector: str, selector_name: str) -> Locator:
        """Find an element on the page."""
        logger.debug(f"[{self.index}] [{self.channel_name}] Looking for element: {selector_name} : {selector}")

        element: Locator = self.page.locator(selector)
        try:
            await element.wait_for(state="visible")
            logger.debug(f"[{self.index}] [{self.channel_name}] Element found: {selector_name} : {selector}")
        except PlaywrightTimeoutError as e:
            logger.debug(f"[{self.index}] [{self.channel_name}] Element not found: {selector_name} : {selector}")
            raise ElementNotFound from e

        return element

    async def find_and_click_element(
        self, selector: str, selector_name: str, for_subscribe: bool = False, check_brand_account: bool = False
    ) -> bool | None:
        """Find an element and click it."""
        brand_account: bool = False
        
        try:
            element: Locator = await self.find_element(selector, selector_name)
            if check_brand_account:
                item = self.page.locator(selector, has_text="You're an owner")
                if await item.count() > 0:
                    brand_account = True

            signin_url: str | None = None
            is_selected: str | None = None
            if self._is_obscura and selector_name == "channel_element":
                signin_url = await element.get_attribute("data-signin-url")
                is_selected = await element.get_attribute("data-is-selected")
                    
            await element.click()
            logger.debug(f"[{self.index}] [{self.channel_name}] Element clicked: {selector_name} : {selector}")

            if self._is_obscura:
                if selector_name == "channel_element" and signin_url and is_selected != "true":
                    target_signin = f"https://www.youtube.com{signin_url}" if signin_url.startswith("/") else signin_url
                    logger.debug(f"[{self.index}] [{self.channel_name}] Switching Obscura channel session via: {target_signin}")
                    await self.go_to_page(target_signin)
                elif selector_name == "subscribe_button":
                    await self.page.evaluate(
                        "async () => { if (window.__obscuraLastActionPromise) await window.__obscuraLastActionPromise; }"
                    )

            if check_brand_account:
                return brand_account
                
        except ElementNotFound as e:
            if not for_subscribe:
                logger.error(f"[{self.index}] [{self.channel_name}] Element not found: {selector_name} : {selector}")
                
                await self.close_browser(reason="Element not found")
                raise BrowserClosedError from e

            if check_brand_account:
                return brand_account
            

    async def type_and_enter(self, text_field: Locator, message: str) -> None:
        """Type a message into a text field and press enter."""
        logger.debug(f"[{self.index}] [{self.channel_name}] Typing message into field: '{message[:50]}{'...' if len(message) > 50 else ''}'")

        await text_field.fill(message)
        await text_field.press("Enter")

        if self._is_obscura:
            send_res = await self.page.evaluate(
                "async () => { if (window.__obscuraLastSendPromise) return await window.__obscuraLastSendPromise; return null; }"
            )
            if isinstance(send_res, dict) and not send_res.get("ok", True):
                logger.warning(f"[{self.index}] [{self.channel_name}] Obscura live chat send status: {send_res.get('status')}")
        
        logger.debug(f"[{self.index}] [{self.channel_name}] Message typed and Enter pressed")

    async def close_browser(self, reason: str = "Reason is unspecified") -> None:
        """Properly close all browser resources to prevent memory leaks."""
        logger.info(f"[{self.index}] [{self.channel_name}] Closing browser: {reason}")
        
        try:
            if hasattr(self, 'page') and self.page:
                try:
                    await self.page.close()
                except Exception as e:
                    logger.debug(f"[{self.index}] [{self.channel_name}] Error closing page: {e}")
            
            if hasattr(self, 'browser_context') and self.browser_context:
                try:
                    await self.browser_context.close()
                except Exception as e:
                    logger.debug(f"[{self.index}] [{self.channel_name}] Error closing browser_context: {e}")
            
            if hasattr(self, 'browser') and self.browser:
                try:
                    await self.browser.close()
                except Exception as e:
                    logger.debug(f"[{self.index}] [{self.channel_name}] Error closing browser: {e}")
            
            if hasattr(self, 'playwright') and self.playwright:
                async with Playwright._playwright_lock:
                    if self.playwright is Playwright._shared_playwright:
                        Playwright._shared_playwright_refcount -= 1
                        if Playwright._shared_playwright_refcount <= 0:
                            try:
                                await Playwright._shared_playwright.stop()
                            except Exception as e:
                                logger.debug(f"[{self.index}] [{self.channel_name}] Error stopping shared playwright: {e}")
                            Playwright._shared_playwright = None
                            Playwright._shared_playwright_refcount = 0
                    else:
                        try:
                            await self.playwright.stop()
                        except Exception as e:
                            logger.debug(f"[{self.index}] [{self.channel_name}] Error stopping playwright: {e}")
                    self.playwright = None
                    
            logger.debug(f"[{self.index}] [{self.channel_name}] Browser resources cleaned up")
        except Exception as e:
            logger.error(f"[{self.index}] [{self.channel_name}] Error during browser cleanup: {e}")


__all__: list[str] = ["Playwright"]

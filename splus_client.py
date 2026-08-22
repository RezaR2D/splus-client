import os
import time
import base64
import mimetypes
import threading
from pathlib import Path

import requests


class SPlusClient:
    """
    کلاینت Selenium برای web.splus.ir
    - ارسال پیام و فایل (با قابلیت پاسخ واقعی)
    - دریافت آپدیت‌های real-time
    - فیلتر پیام‌های خود کاربر
    """

    def __init__(self, driver, display_logs=True):
        self.driver = driver
        self.display_logs = bool(display_logs)

        self._initialized = False
        self._module_id = None
        self._lock = threading.RLock()
        self._update_hook_installed = False
        self._own_user_id = None

    def _log(self, *args, **kwargs):
        if self.display_logs:
            print(*args, **kwargs)

    # ------------------------------------------------------------------
    # پیدا کردن manager / actions
    # ------------------------------------------------------------------

    def _initialize(self):
        if self._initialized:
            return

        self._log("🔍 Searching SPlus manager...")
        try:
            self.driver.set_script_timeout(120)
        except Exception:
            pass

        result = self.driver.execute_async_script("""
            const done = arguments[arguments.length - 1];

            (async () => {
                try {
                    let wp = null;

                    for (let i = 0; i < 60; i++) {
                        try {
                            window.webpackChunkSoroushPlus = window.webpackChunkSoroushPlus || [];
                            window.webpackChunkSoroushPlus.push([
                                [Date.now()], {},
                                function(require) { wp = require; }
                            ]);
                        } catch (e) {}

                        if (wp) break;
                        await new Promise(r => setTimeout(r, 250));
                    }

                    if (!wp) {
                        done({ ok: false, error: "webpack require پیدا نشد" });
                        return;
                    }

                    const ids = Object.keys(wp.m || {});
                    let selected = null;

                    for (const id of ids) {
                        try {
                            const mod = wp(id);
                            if (mod && typeof mod.ko === "function") {
                                const manager = mod.ko();
                                if (manager && typeof manager.sendMessage === "function") {
                                    selected = {
                                        moduleId: id,
                                        exportName: "ko",
                                        manager,
                                        hasUpdateDraft: typeof manager.updateDraftReplyInfo === "function",
                                        hasOpenChat: typeof manager.openChat === "function"
                                    };
                                    break;
                                }
                            }
                        } catch (e) {}
                    }

                    if (!selected) {
                        for (const id of ids) {
                            try {
                                const mod = wp(id);
                                if (!mod || typeof mod !== "object") continue;
                                for (const [key, fn] of Object.entries(mod)) {
                                    if (typeof fn !== "function") continue;
                                    try {
                                        const manager = fn();
                                        if (manager && typeof manager.sendMessage === "function") {
                                            selected = {
                                                moduleId: id,
                                                exportName: key,
                                                manager,
                                                hasUpdateDraft: typeof manager.updateDraftReplyInfo === "function",
                                                hasOpenChat: typeof manager.openChat === "function"
                                            };
                                            break;
                                        }
                                    } catch (e) {}
                                }
                                if (selected) break;
                            } catch (e) {}
                        }
                    }

                    if (!selected) {
                        done({ ok: false, error: "manager دارای sendMessage پیدا نشد" });
                        return;
                    }

                    window.__splus_manager = selected.manager;
                    window.__splus_wp = wp;
                    window.__splus_attachments = window.__splus_attachments || {};

                    done({
                        ok: true,
                        moduleId: selected.moduleId,
                        exportName: selected.exportName,
                        hasUpdateDraft: selected.hasUpdateDraft,
                        hasOpenChat: selected.hasOpenChat
                    });
                } catch (err) {
                    done({ ok: false, error: String(err) });
                }
            })();
        """)

        if not result or not result.get("ok"):
            raise RuntimeError("❌ SPlus initialization failed: " + str(result))

        self._module_id = result["moduleId"]
        self._initialized = True
        self._log(
            f"✅ Manager ready (module={result['moduleId']}, "
            f"export={result.get('exportName')}, "
            f"draft={result.get('hasUpdateDraft')}, "
            f"openChat={result.get('hasOpenChat')})"
        )

    # ------------------------------------------------------------------
    # شناسه کاربر جاری
    # ------------------------------------------------------------------

    def _get_own_user_id(self):
        if self._own_user_id:
            return self._own_user_id

        uid = self.driver.execute_script("""
            try {
                if (window.__splus_own_user_id) return window.__splus_own_user_id;

                const gs = localStorage.getItem("sp-global-state");
                if (gs) {
                    const s = JSON.parse(gs);
                    if (s && s.currentUserId) {
                        window.__splus_own_user_id = String(s.currentUserId);
                        return window.__splus_own_user_id;
                    }
                }

                const acc = localStorage.getItem("account1");
                if (acc) {
                    const a = JSON.parse(acc);
                    if (a && a.userId) {
                        window.__splus_own_user_id = String(a.userId);
                        return window.__splus_own_user_id;
                    }
                }
                return null;
            } catch (e) { return null; }
        """)

        self._own_user_id = uid
        return uid

    # ------------------------------------------------------------------
    # ست کردن ریپلای روی Draft (کلید اصلی)
    # ------------------------------------------------------------------

    def _set_reply_draft(self, chat_id, reply_to, thread_id=-1):
        """
        ریپلای در SPlus از طریق Draft انجام می‌شود.
        updateDraftReplyInfo روی چت باز فعلی کار می‌کند،
        پس قبلش openChat صدا می‌زنیم.
        """
        result = self.driver.execute_async_script("""
            const done = arguments[arguments.length - 1];
            const chatId = String(arguments[0]);
            const replyTo = Number(arguments[1]);
            const threadId = arguments[2];

            (async () => {
                try {
                    const manager = window.__splus_manager;
                    if (!manager) {
                        done({ ok: false, error: "manager پیدا نشد" });
                        return;
                    }

                    // باز کردن چت تا Draft روی همان چت ست شود
                    if (typeof manager.openChat === "function") {
                        try {
                            manager.openChat({ id: chatId });
                        } catch (e) {}
                        await new Promise(r => setTimeout(r, 350));
                    }

                    if (typeof manager.updateDraftReplyInfo !== "function") {
                        done({ ok: false, error: "updateDraftReplyInfo وجود ندارد" });
                        return;
                    }

                    manager.updateDraftReplyInfo({
                        replyToMsgId: replyTo,
                        quoteOffset: -1,
                        quoteText: undefined
                    });

                    await new Promise(r => setTimeout(r, 150));
                    done({ ok: true });
                } catch (e) {
                    done({ ok: false, error: String(e) });
                }
            })();
        """, str(chat_id), int(reply_to), thread_id)

        if not result or not result.get("ok"):
            self._log("⚠️ ست کردن Draft ریپلای ناموفق:", result)
            return False

        return True

    # ------------------------------------------------------------------
    # هوک آپدیت سبک (غیرمخرب)
    # ------------------------------------------------------------------

    def _install_update_hook(self):
        if self._update_hook_installed:
            return

        self.driver.execute_script("""
            if (window.__splus_update_hook_installed) return;

            window.__splus_update_queue = window.__splus_update_queue || [];

            window.webpackChunkSoroushPlus = window.webpackChunkSoroushPlus || [];
            window.webpackChunkSoroushPlus.push([
                [Math.random()],
                {},
                function(req) {
                    for (let i = 0; i < 30000; i++) {
                        try {
                            const m = req(i);
                            if (m && typeof m.aJ === "function") {
                                m.aJ("apiUpdate", function(g, a, update) {
                                    try {
                                        if (update && update["@type"] === "newMessage") {
                                            window.__splus_update_queue.push(update);
                                        }
                                    } catch (e) {}
                                });
                                window.__splus_update_hook_installed = true;
                                return;
                            }
                        } catch (e) {}
                    }
                }
            ]);
        """)

        time.sleep(1.2)
        ok = self.driver.execute_script("return !!window.__splus_update_hook_installed;")
        if not ok:
            raise RuntimeError("❌ نصب هوک آپدیت ناموفق")

        self._update_hook_installed = True
        self._log("✅ هوک آپدیت نصب شد (سبک و غیرمخرب)")

    # ------------------------------------------------------------------
    # دریافت آپدیت‌ها
    # ------------------------------------------------------------------

    def listen_for_updates(self, handler, self_messages=False, poll_interval=0.35):
        self._install_update_hook()
        own_id = self._get_own_user_id()

        self._log(f"👤 Own ID: {own_id}")
        self._log(f"📥 در حال گوش دادن به آپدیت‌ها (self_messages={self_messages})")
        self._log("برای توقف: exit\n")

        stop = threading.Event()

        def watcher():
            while not stop.is_set():
                try:
                    if input().strip().lower() == "exit":
                        stop.set()
                        self._log("\n🛑 متوقف شد...")
                        break
                except Exception:
                    break

        threading.Thread(target=watcher, daemon=True).start()

        try:
            while not stop.is_set():
                updates = self.driver.execute_script("""
                    const q = window.__splus_update_queue || [];
                    window.__splus_update_queue = [];
                    return q;
                """) or []

                for update in updates:
                    if not isinstance(update, dict):
                        continue
                    if update.get("@type") != "newMessage":
                        continue

                    msg = update.get("message") or update
                    sender = str(msg.get("senderId") or "")
                    chat_id = str(msg.get("chatId") or update.get("chatId") or "")
                    msg_id = msg.get("id") or update.get("id")

                    if not self_messages and own_id and sender == str(own_id):
                        continue

                    try:
                        handler(update=update, chat_id=chat_id, message_id=msg_id)
                    except Exception as e:
                        self._log("❌ خطا در handler:", e)

                time.sleep(poll_interval)
        finally:
            stop.set()
            self._log("✅ گوش دادن به آپدیت‌ها متوقف شد")

    # ------------------------------------------------------------------
    # ارسال پیام متنی (با ریپلای واقعی)
    # ------------------------------------------------------------------

    def send_message(self, chat_id, text, thread_id=-1, is_silent=False, reply_to=None):
        with self._lock:
            self._initialize()

            # کلید حل مشکل ریپلای: اول Draft ست شود
            if reply_to is not None:
                ok = self._set_reply_draft(chat_id, reply_to, thread_id=thread_id)
                if not ok:
                    self._log("⚠️ ادامه بدون Draft (ممکن است ریپلای نشود)")

            payload = {
                "messageList": {
                    "chatId": str(chat_id),
                    "type": "thread",
                    "threadId": thread_id
                },
                "text": text,
                "isSilent": bool(is_silent),
                "shouldUpdateStickerSetOrder": True
            }
            # عمداً replyInfo داخل payload نمی‌گذاریم؛
            # sendMessage از Draft می‌خواند.

            result = self.driver.execute_script("""
                const msg = arguments[0];
                const manager = window.__splus_manager;
                if (!manager) return { ok: false, error: "manager پیدا نشد" };
                try {
                    manager.sendMessage(msg);
                    return { ok: true };
                } catch (e) {
                    return { ok: false, error: String(e) };
                }
            """, payload)

            if not result or not result.get("ok"):
                raise RuntimeError("❌ sendMessage failed: " + str(result))

            extra = f" (پاسخ به {reply_to})" if reply_to else ""
            self._log(f"📨 پیام ارسال شد{extra}")
            return result

    # ------------------------------------------------------------------
    # دانلود فایل
    # ------------------------------------------------------------------

    def _download_file(self, url, download_dir="downloads"):
        os.makedirs(download_dir, exist_ok=True)
        self._log(f"📥 دانلود از: {url}")

        r = requests.get(
            url, stream=True, timeout=120,
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0"}
        )
        r.raise_for_status()

        filename = None
        cd = r.headers.get("Content-Disposition", "")
        if "filename=" in cd:
            filename = cd.split("filename=", 1)[1].strip().strip('"').strip("'")

        if not filename:
            filename = os.path.basename(url.split("?", 1)[0]) or f"file_{int(time.time()*1000)}"

        ct = r.headers.get("Content-Type", "")
        low = filename.lower()
        if "image/jpeg" in ct and not low.endswith((".jpg", ".jpeg")):
            filename += ".jpg"
        elif "image/png" in ct and not low.endswith(".png"):
            filename += ".png"
        elif "image/webp" in ct and not low.endswith(".webp"):
            filename += ".webp"

        path = os.path.join(
            download_dir,
            f"{Path(filename).stem}_{int(time.time()*1000)}_{os.getpid()}{Path(filename).suffix}"
        )

        with open(path, "wb") as f:
            for chunk in r.iter_content(1024 * 1024):
                if chunk:
                    f.write(chunk)

        self._log(f"✅ دانلود شد: {path}")
        return path

    # ------------------------------------------------------------------
    # ساخت attachment کامل
    # ------------------------------------------------------------------

    def _create_attachment(self, filepath):
        filename = os.path.basename(filepath)
        mime = mimetypes.guess_type(filename)[0] or "application/octet-stream"

        with open(filepath, "rb") as f:
            data = f.read()

        b64 = base64.b64encode(data).decode("ascii")
        self._log(f"📎 ساخت attachment: {filename} ({len(data)} بایت)")

        try:
            self.driver.set_script_timeout(120)
        except Exception:
            pass

        result = self.driver.execute_async_script("""
            const done = arguments[arguments.length - 1];
            const b64 = arguments[0], filename = arguments[1], mimeType = arguments[2];

            (async () => {
                try {
                    const bin = atob(b64);
                    const bytes = new Uint8Array(bin.length);
                    for (let i = 0; i < bin.length; i++) bytes[i] = bin.charCodeAt(i);

                    const blob = new Blob([bytes], { type: mimeType });
                    const file = new File([blob], filename, { type: mimeType, lastModified: Date.now() });
                    const blobUrl = URL.createObjectURL(file);

                    let quick, previewBlobUrl = blobUrl, shouldSendAsFile, compressedBlobUrl;
                    let finalName = filename, finalMime = mimeType;

                    if (mimeType.startsWith("image/")) {
                        const img = await new Promise((res, rej) => {
                            const i = new Image();
                            i.onload = () => res(i);
                            i.onerror = () => rej(new Error("img fail"));
                            i.src = blobUrl;
                        });

                        const w = img.naturalWidth || img.width;
                        const h = img.naturalHeight || img.height;
                        const ratio = Math.max(w, h) / Math.min(w, h);

                        if (ratio > 20) {
                            shouldSendAsFile = true;
                        } else {
                            quick = { width: w, height: h };
                            const maxSide = Math.max(w, h);

                            if (maxSide > 40) {
                                const s = 40 / maxSide;
                                const c = document.createElement("canvas");
                                c.width = Math.max(1, Math.round(w * s));
                                c.height = Math.max(1, Math.round(h * s));
                                c.getContext("2d").drawImage(img, 0, 0, c.width, c.height);
                                previewBlobUrl = c.toDataURL("image/jpeg", 0.7);
                            }

                            if (maxSide > 1280 && mimeType !== "image/gif") {
                                const s = 1280 / maxSide;
                                const c = document.createElement("canvas");
                                c.width = Math.max(1, Math.round(w * s));
                                c.height = Math.max(1, Math.round(h * s));
                                c.getContext("2d").drawImage(img, 0, 0, c.width, c.height);
                                compressedBlobUrl = await new Promise(r => {
                                    c.toBlob(b => r(b ? URL.createObjectURL(b) : null), "image/jpeg", 0.85);
                                });
                                if (mimeType === "image/png" || mimeType === "image/webp") {
                                    finalName = finalName.replace(/\\.[^.]+$/, ".jpg");
                                    finalMime = "image/jpeg";
                                }
                            }
                        }
                    }

                    if (mimeType.startsWith("video/")) {
                        try {
                            const v = document.createElement("video");
                            v.preload = "metadata"; v.muted = true; v.src = blobUrl;
                            await new Promise((res, rej) => {
                                v.onloadedmetadata = res;
                                v.onerror = () => rej();
                                setTimeout(() => rej(), 8000);
                            });
                            const vw = v.videoWidth || 0, vh = v.videoHeight || 0;
                            if (!vw || !vh) shouldSendAsFile = true;
                            else {
                                const ratio = Math.max(vw, vh) / Math.min(vw, vh);
                                if (ratio > 20) shouldSendAsFile = true;
                                else quick = { width: vw, height: vh, duration: v.duration || 0 };
                            }
                        } catch (e) {
                            shouldSendAsFile = true;
                        }
                    }

                    const uniqueId = crypto.randomUUID
                        ? crypto.randomUUID()
                        : (Date.now() + "-" + Math.random().toString(16).slice(2));

                    const attachment = {
                        blobUrl: compressedBlobUrl || blobUrl,
                        previewBlobUrl,
                        filename: finalName,
                        mimeType: finalMime,
                        size: file.size,
                        uniqueId,
                        quick,
                        shouldSendAsFile: shouldSendAsFile || undefined
                    };

                    window.__splus_attachments = window.__splus_attachments || {};
                    window.__splus_attachments[uniqueId] = {
                        attachment, originalBlobUrl: blobUrl, compressedBlobUrl
                    };

                    done({ ok: true, attachment });
                } catch (e) {
                    done({ ok: false, error: String(e) });
                }
            })();
        """, b64, filename, mime)

        if not result or not result.get("ok"):
            raise RuntimeError("❌ ساخت attachment ناموفق: " + str(result))

        self._log("✅ Attachment آماده شد")
        return result["attachment"]

    # ------------------------------------------------------------------
    # ارسال فایل (با ریپلای واقعی)
    # ------------------------------------------------------------------

    def send_file(self, chat_id, source, thread_id=-1, caption="", is_silent=False, reply_to=None):
        downloaded = False
        path = None

        try:
            if isinstance(source, str) and source.startswith(("http://", "https://")):
                path = self._download_file(source)
                downloaded = True
            else:
                path = os.path.abspath(os.path.expanduser(source))

            if not os.path.isfile(path):
                raise FileNotFoundError(path)

            with self._lock:
                self._initialize()

                if reply_to is not None:
                    ok = self._set_reply_draft(chat_id, reply_to, thread_id=thread_id)
                    if not ok:
                        self._log("⚠️ ادامه بدون Draft (ممکن است ریپلای نشود)")

                att = self._create_attachment(path)

                payload = {
                    "messageList": {
                        "chatId": str(chat_id),
                        "type": "thread",
                        "threadId": thread_id
                    },
                    "text": caption or "",
                    "attachments": [att],
                    "isSilent": bool(is_silent),
                    "shouldGroupMessages": True,
                    "shouldUpdateStickerSetOrder": True
                }

                result = self.driver.execute_script("""
                    const msg = arguments[0];
                    const manager = window.__splus_manager;
                    if (!manager || typeof manager.sendMessage !== "function")
                        return { ok: false, error: "manager پیدا نشد" };
                    try {
                        manager.sendMessage(msg);
                        return { ok: true };
                    } catch (e) {
                        return { ok: false, error: String(e) };
                    }
                """, payload)

                if not result or not result.get("ok"):
                    raise RuntimeError("❌ ارسال فایل ناموفق: " + str(result))

                extra = f" (پاسخ به {reply_to})" if reply_to else ""
                self._log(f"✅ فایل ارسال شد{extra}")

                self.driver.execute_script("""
                    const id = arguments[0];
                    setTimeout(() => {
                        try {
                            const s = window.__splus_attachments;
                            if (!s || !s[id]) return;
                            const it = s[id];
                            if (it.originalBlobUrl) URL.revokeObjectURL(it.originalBlobUrl);
                            if (it.compressedBlobUrl) URL.revokeObjectURL(it.compressedBlobUrl);
                            delete s[id];
                        } catch (e) {}
                    }, 180000);
                """, att.get("uniqueId"))

                time.sleep(1.5)
                return result

        finally:
            if downloaded and path and os.path.isfile(path):
                try:
                    os.remove(path)
                except Exception:
                    pass

    def _normalize_message_id(self, message_id):
        if message_id is None:
            raise ValueError("message_id is empty")
        if isinstance(message_id, (int, float)):
            return message_id
        s = str(message_id).strip()
        try:
            return float(s) if "." in s else int(s)
        except Exception:
            return s

    def _as_id_list(self, message_id):
        if message_id is None:
            raise ValueError("message_id is empty")
        items = message_id if isinstance(message_id, (list, tuple, set)) else [message_id]
        return [self._normalize_message_id(x) for x in items]

    def _open_chat(self, chat_id, wait=1.2):
        self.driver.execute_script("""
            const m = window.__splus_manager;
            const id = String(arguments[0]);
            if (!m) return;
            try {
                if (typeof m.openChat === "function") m.openChat({ id: id });
                else if (typeof m.openThread === "function") m.openThread({ chatId: id, threadId: -1 });
            } catch (e) {}
        """, str(chat_id))
        time.sleep(wait)

    def _call_manager(self, method_name, payload):
        return self.driver.execute_script("""
            const manager = window.__splus_manager;
            const method = arguments[0];
            const payload = arguments[1];
            if (!manager || typeof manager[method] !== "function")
                return { ok: false, error: method + " not found" };
            try {
                manager[method](payload);
                return { ok: true };
            } catch (e) {
                return { ok: false, error: String(e) };
            }
        """, method_name, payload)

    def pin_message(self, chat_id, message_id, one_side=False, silent=False, open_chat=True):
        with self._lock:
            self._initialize()
            if open_chat:
                self._open_chat(chat_id)

            ids = self._as_id_list(message_id)
            for mid in ids:
                payload = {"messageId": mid, "isUnpin": False}
                if one_side:
                    payload["isOneSide"] = True
                    payload["isSilent"] = True
                elif silent:
                    payload["isSilent"] = True

                result = self._call_manager("pinMessage", payload)
                if not result or not result.get("ok"):
                    raise RuntimeError("pin_message failed: " + str(result))

            self._log(f"📌 pin: {ids} (chat={chat_id})")
            return {"ok": True, "ids": ids}

    def unpin_message(self, chat_id, message_id, open_chat=True):
        with self._lock:
            self._initialize()
            if open_chat:
                self._open_chat(chat_id)

            ids = self._as_id_list(message_id)
            for mid in ids:
                result = self._call_manager("pinMessage", {
                    "messageId": mid,
                    "isUnpin": True
                })
                if not result or not result.get("ok"):
                    raise RuntimeError("unpin_message failed: " + str(result))

            self._log(f"📌 unpin: {ids} (chat={chat_id})")
            return {"ok": True, "ids": ids}

    def delete_message(self, chat_id, message_id, for_all=False, open_chat=True):
        with self._lock:
            self._initialize()
            if open_chat:
                self._open_chat(chat_id)

            ids = self._as_id_list(message_id)
            result = self._call_manager("deleteMessages", {
                "messageIds": ids,
                "shouldDeleteForAll": bool(for_all)
            })
            if not result or not result.get("ok"):
                raise RuntimeError("delete_message failed: " + str(result))

            self._log(f"🗑 delete: {ids} (chat={chat_id}, for_all={for_all})")
            return result
        
    def send_file_with_caption(self, chat_id, source, caption, thread_id=-1, is_silent=False, reply_to=None):
        return self.send_file(
            chat_id=chat_id,
            source=source,
            thread_id=thread_id,
            caption=caption,
            is_silent=is_silent,
            reply_to=reply_to
        )
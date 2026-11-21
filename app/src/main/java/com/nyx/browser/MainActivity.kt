package com.nyx.browser

import android.app.Activity
import android.app.AlertDialog
import android.app.DownloadManager
import android.content.Context
import android.content.Intent
import android.graphics.Color
import android.graphics.Typeface
import android.graphics.drawable.GradientDrawable
import android.net.Uri
import android.os.Build
import android.os.Bundle
import android.os.Environment
import android.view.Gravity
import android.view.View
import android.view.ViewGroup
import android.view.WindowInsets
import android.view.inputmethod.EditorInfo
import android.webkit.CookieManager
import android.webkit.DownloadListener
import android.webkit.PermissionRequest
import android.webkit.SslErrorHandler
import android.webkit.URLUtil
import android.webkit.ValueCallback
import android.webkit.WebChromeClient
import android.webkit.WebResourceRequest
import android.webkit.WebSettings
import android.webkit.WebView
import android.webkit.WebViewClient
import android.widget.ArrayAdapter
import android.widget.AutoCompleteTextView
import android.widget.FrameLayout
import android.widget.HorizontalScrollView
import android.widget.LinearLayout
import android.widget.ProgressBar
import android.widget.TextView
import android.widget.Toast
import org.json.JSONArray
import org.json.JSONObject

class MainActivity : Activity() {
    private data class BrowserEntry(val title: String, val url: String)
    private data class BrowserTab(
        val id: Int,
        val webView: WebView,
        var title: String,
        var url: String
    )

    private val tabs = mutableListOf<BrowserTab>()
    private var nextTabId = 1
    private var currentTabId = -1
    private var pendingFileUpload: ValueCallback<Array<Uri>>? = null

    private lateinit var root: LinearLayout
    private lateinit var tabStrip: LinearLayout
    private lateinit var webContainer: FrameLayout
    private lateinit var address: AutoCompleteTextView
    private lateinit var progress: ProgressBar
    private lateinit var backButton: TextView
    private lateinit var forwardButton: TextView
    private lateinit var reloadButton: TextView
    private lateinit var suggestionAdapter: ArrayAdapter<String>

    private val prefs by lazy { getSharedPreferences("nyx_browser", Context.MODE_PRIVATE) }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        window.statusBarColor = Color.rgb(9, 8, 17)
        window.navigationBarColor = Color.rgb(9, 8, 17)
        window.decorView.systemUiVisibility = 0
        applySystemBarInsets()
        buildInterface()
        createTab(savedInstanceState?.getString(STATE_URL))
    }

    private fun applySystemBarInsets() {
        if (Build.VERSION.SDK_INT >= 35) {
            window.decorView.setOnApplyWindowInsetsListener { view, insets ->
                val safe = insets.getInsets(
                    WindowInsets.Type.systemBars() or WindowInsets.Type.displayCutout()
                )
                view.setPadding(safe.left, safe.top, safe.right, safe.bottom)
                insets
            }
            window.decorView.requestApplyInsets()
        }
    }

    private fun buildInterface() {
        root = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            setBackgroundColor(C_BG)
            setPadding(dp(10), dp(7), dp(10), dp(5))
        }

        val brandRow = LinearLayout(this).apply {
            orientation = LinearLayout.HORIZONTAL
            gravity = Gravity.CENTER_VERTICAL
        }
        val brand = TextView(this).apply {
            text = "N  NYX BROWSER"
            textSize = 16f
            setTextColor(C_TEXT)
            typeface = Typeface.create("sans-serif", Typeface.BOLD)
            letterSpacing = 0.06f
            setPadding(dp(5), dp(7), dp(5), dp(7))
        }
        val brandSpacer = View(this)
        val newTabTop = button("+", 40, 38)
        newTabTop.contentDescription = "Новая вкладка"
        newTabTop.setOnClickListener { createTab() }
        brandRow.addView(brand, LinearLayout.LayoutParams(0, dp(42), 1f))
        brandRow.addView(newTabTop)
        root.addView(brandRow)

        val tabScroll = HorizontalScrollView(this).apply {
            isHorizontalScrollBarEnabled = false
            overScrollMode = View.OVER_SCROLL_NEVER
        }
        tabStrip = LinearLayout(this).apply {
            orientation = LinearLayout.HORIZONTAL
            gravity = Gravity.CENTER_VERTICAL
        }
        tabScroll.addView(tabStrip)
        root.addView(tabScroll, LinearLayout.LayoutParams(
            ViewGroup.LayoutParams.MATCH_PARENT, dp(43)
        ))

        val toolbar = LinearLayout(this).apply {
            orientation = LinearLayout.HORIZONTAL
            gravity = Gravity.CENTER_VERTICAL
        }
        backButton = button("‹", 36, 42).also { it.setOnClickListener { goBack() } }
        forwardButton = button("›", 36, 42).also { it.setOnClickListener { goForward() } }
        reloadButton = button("↻", 36, 42).also { it.setOnClickListener { reloadCurrent() } }
        address = AutoCompleteTextView(this).apply {
            setSingleLine(true)
            textSize = 13f
            setTextColor(C_TEXT)
            setHintTextColor(C_MUTED)
            hint = "Поиск или адрес сайта"
            inputType = android.text.InputType.TYPE_CLASS_TEXT or
                android.text.InputType.TYPE_TEXT_VARIATION_URI
            imeOptions = EditorInfo.IME_ACTION_GO
            threshold = 1
            dropDownHeight = dp(270)
            setPadding(dp(12), 0, dp(8), 0)
            background = rounded(C_PANEL, C_LINE, 13)
        }
        suggestionAdapter = ArrayAdapter(this, android.R.layout.simple_dropdown_item_1line, mutableListOf())
        address.setAdapter(suggestionAdapter)
        address.setOnItemClickListener { _, _, position, _ ->
            val selected = suggestionAdapter.getItem(position)
            if (!selected.isNullOrBlank()) navigateInput(selected)
        }
        address.setOnEditorActionListener { _, actionId, _ ->
            if (actionId == EditorInfo.IME_ACTION_GO || actionId == EditorInfo.IME_ACTION_DONE) {
                navigateInput(address.text.toString())
                true
            } else false
        }
        address.addTextChangedListener(object : android.text.TextWatcher {
            override fun beforeTextChanged(s: CharSequence?, start: Int, count: Int, after: Int) = Unit
            override fun onTextChanged(s: CharSequence?, start: Int, before: Int, count: Int) {
                refreshSuggestions(s?.toString().orEmpty())
            }
            override fun afterTextChanged(s: android.text.Editable?) = Unit
        })
        val go = button("↵", 38, 42).also { it.setOnClickListener { navigateInput(address.text.toString()) } }

        toolbar.addView(backButton, LinearLayout.LayoutParams(dp(36), dp(42)))
        toolbar.addView(forwardButton, LinearLayout.LayoutParams(dp(36), dp(42)).apply {
            marginStart = dp(3)
        })
        toolbar.addView(reloadButton, LinearLayout.LayoutParams(dp(36), dp(42)).apply {
            marginStart = dp(3)
        })
        toolbar.addView(address, LinearLayout.LayoutParams(0, dp(42), 1f).apply {
            marginStart = dp(5)
        })
        toolbar.addView(go, LinearLayout.LayoutParams(dp(38), dp(42)).apply {
            marginStart = dp(4)
        })
        root.addView(toolbar, LinearLayout.LayoutParams(
            ViewGroup.LayoutParams.MATCH_PARENT, dp(50)
        ))

        progress = ProgressBar(this, null, android.R.attr.progressBarStyleHorizontal).apply {
            max = 100
            progress = 0
            progressTintList = android.content.res.ColorStateList.valueOf(C_ACCENT)
            progressBackgroundTintList = android.content.res.ColorStateList.valueOf(C_LINE)
            visibility = View.GONE
        }
        root.addView(progress, LinearLayout.LayoutParams(
            ViewGroup.LayoutParams.MATCH_PARENT, dp(3)
        ))

        webContainer = FrameLayout(this).apply {
            setBackgroundColor(C_BG)
        }
        root.addView(webContainer, LinearLayout.LayoutParams(
            ViewGroup.LayoutParams.MATCH_PARENT, 0, 1f
        ))

        val bottom = LinearLayout(this).apply {
            orientation = LinearLayout.HORIZONTAL
            gravity = Gravity.CENTER
            setPadding(0, dp(5), 0, dp(2))
        }
        val home = button("⌂  Главная", 0, 42)
        val bookmarks = button("☆", 42, 42)
        val history = button("◷", 42, 42)
        val share = button("↗", 42, 42)
        home.setOnClickListener { showHome() }
        bookmarks.setOnClickListener { showEntries(KEY_BOOKMARKS, "Закладки") }
        history.setOnClickListener { showEntries(KEY_HISTORY, "История") }
        share.setOnClickListener { shareCurrentPage() }
        bottom.addView(home, LinearLayout.LayoutParams(0, dp(42), 1f))
        bottom.addView(bookmarks, LinearLayout.LayoutParams(dp(42), dp(42)).apply {
            marginStart = dp(5)
        })
        bottom.addView(history, LinearLayout.LayoutParams(dp(42), dp(42)).apply {
            marginStart = dp(5)
        })
        bottom.addView(share, LinearLayout.LayoutParams(dp(42), dp(42)).apply {
            marginStart = dp(5)
        })
        root.addView(bottom)
        setContentView(root)
    }

    private fun createTab(initialUrl: String? = null) {
        if (tabs.size >= MAX_TABS) {
            toast("Открыто максимальное количество вкладок")
            return
        }
        val webView = WebView(this)
        configureWebView(webView)
        val tab = BrowserTab(nextTabId++, webView, "Новая вкладка", HOME_URL)
        tabs.add(tab)
        webContainer.addView(webView, FrameLayout.LayoutParams(
            ViewGroup.LayoutParams.MATCH_PARENT,
            ViewGroup.LayoutParams.MATCH_PARENT
        ))
        switchTo(tab.id)
        if (!initialUrl.isNullOrBlank()) {
            webView.loadUrl(initialUrl)
        } else {
            loadHome(tab)
        }
    }

    private fun configureWebView(webView: WebView) {
        webView.setBackgroundColor(C_BG)
        webView.setLayerType(View.LAYER_TYPE_HARDWARE, null)
        webView.settings.apply {
            javaScriptEnabled = true
            domStorageEnabled = true
            databaseEnabled = true
            loadsImagesAutomatically = true
            useWideViewPort = true
            loadWithOverviewMode = true
            setSupportZoom(true)
            builtInZoomControls = true
            displayZoomControls = false
            allowFileAccess = false
            allowContentAccess = true
            javaScriptCanOpenWindowsAutomatically = false
            setSupportMultipleWindows(false)
            mixedContentMode = WebSettings.MIXED_CONTENT_NEVER_ALLOW
            if (Build.VERSION.SDK_INT >= 26) safeBrowsingEnabled = true
        }
        CookieManager.getInstance().setAcceptCookie(true)

        webView.webViewClient = object : WebViewClient() {
            override fun shouldOverrideUrlLoading(
                view: WebView?,
                request: WebResourceRequest?
            ): Boolean {
                val uri = request?.url ?: return false
                val scheme = uri.scheme?.lowercase().orEmpty()
                if (scheme == "http" || scheme == "https" || scheme == "about" ||
                    scheme == "data" || scheme == "blob") return false
                return openExternal(uri)
            }

            override fun onPageStarted(view: WebView?, url: String?, favicon: android.graphics.Bitmap?) {
                val tab = tabFor(webView) ?: return
                tab.url = url ?: tab.url
                if (tab.id == currentTabId) {
                    progress.progress = 8
                    progress.visibility = View.VISIBLE
                    showAddress(tab.url)
                    updateNavigationButtons()
                }
            }

            override fun onPageFinished(view: WebView?, url: String?) {
                val tab = tabFor(webView) ?: return
                tab.url = url ?: tab.url
                tab.title = view?.title?.takeIf { it.isNotBlank() } ?: titleFor(tab.url)
                if (tab.id == currentTabId) {
                    progress.progress = 100
                    progress.visibility = View.GONE
                    showAddress(tab.url)
                    refreshTabs()
                    updateNavigationButtons()
                }
                if (tab.url.startsWith("https://") || tab.url.startsWith("http://")) {
                    saveEntry(KEY_HISTORY, BrowserEntry(tab.title, tab.url), 100)
                }
            }

            override fun onReceivedSslError(
                view: WebView?,
                handler: SslErrorHandler?,
                error: android.net.http.SslError?
            ) {
                handler?.cancel()
                toast("NYX заблокировал страницу с ошибкой сертификата")
            }

            override fun onReceivedError(
                view: WebView?,
                request: WebResourceRequest?,
                error: android.webkit.WebResourceError?
            ) {
                if (request?.isForMainFrame == true) {
                    toast("Не удалось загрузить страницу. Проверь подключение.")
                }
            }
        }

        webView.webChromeClient = object : WebChromeClient() {
            override fun onProgressChanged(view: WebView?, newProgress: Int) {
                if (tabFor(webView)?.id == currentTabId) {
                    progress.progress = newProgress
                    progress.visibility = if (newProgress >= 100) View.GONE else View.VISIBLE
                }
            }

            override fun onReceivedTitle(view: WebView?, title: String?) {
                val tab = tabFor(webView) ?: return
                if (!title.isNullOrBlank()) tab.title = title
                if (tab.id == currentTabId) refreshTabs()
            }

            override fun onShowFileChooser(
                webView: WebView?,
                filePathCallback: ValueCallback<Array<Uri>>?,
                fileChooserParams: FileChooserParams?
            ): Boolean {
                pendingFileUpload?.onReceiveValue(null)
                pendingFileUpload = filePathCallback
                val intent = try {
                    fileChooserParams?.createIntent()
                } catch (_: Exception) {
                    null
                } ?: run {
                    pendingFileUpload = null
                    return false
                }
                return try {
                    @Suppress("DEPRECATION")
                    startActivityForResult(intent, FILE_CHOOSER_REQUEST)
                    true
                } catch (_: Exception) {
                    pendingFileUpload = null
                    false
                }
            }

            override fun onPermissionRequest(request: PermissionRequest?) {
                request?.deny()
                toast("Доступ к камере и микрофону пока не включён")
            }

            override fun onGeolocationPermissionsShowPrompt(
                origin: String?,
                callback: android.webkit.GeolocationPermissions.Callback?
            ) {
                callback?.invoke(origin, false, false)
            }
        }

        webView.setDownloadListener(DownloadListener { url, userAgent, contentDisposition, mimeType ->
            startDownload(url, userAgent, contentDisposition, mimeType)
        })
    }

    private fun loadHome(tab: BrowserTab) {
        tab.url = HOME_URL
        tab.title = "NYX — твой браузер"
        tab.webView.loadDataWithBaseURL(
            "https://nyx.local/",
            HOME_HTML,
            "text/html",
            "UTF-8",
            null
        )
        if (tab.id == currentTabId) {
            address.setText("", false)
            refreshTabs()
        }
    }

    private fun showHome() {
        currentTab()?.let { loadHome(it) }
    }

    private fun navigateInput(input: String) {
        val text = input.trim()
        if (text.isEmpty()) return
        val hasScheme = Regex("^[a-zA-Z][a-zA-Z0-9+.-]*:").containsMatchIn(text)
        val isHost = !text.contains(" ") && text.contains(".")
        val target = when {
            hasScheme -> text
            isHost -> "https://" + text
            else -> "https://www.google.com/search?q=" + Uri.encode(text)
        }
        val uri = try { Uri.parse(target) } catch (_: Exception) { null }
        if (uri == null) {
            toast("Проверь адрес")
            return
        }
        if (uri.scheme != "http" && uri.scheme != "https") {
            openExternal(uri)
            return
        }
        currentTab()?.webView?.loadUrl(uri.toString()) ?: createTab(uri.toString())
        address.clearFocus()
    }

    private fun goBack() {
        val webView = currentTab()?.webView ?: return
        if (webView.canGoBack()) webView.goBack() else loadHome(currentTab()!!)
    }

    private fun goForward() {
        currentTab()?.webView?.let {
            if (it.canGoForward()) it.goForward()
        }
    }

    private fun reloadCurrent() {
        currentTab()?.webView?.reload()
    }

    private fun switchTo(id: Int) {
        val tab = tabs.firstOrNull { it.id == id } ?: return
        currentTabId = id
        tabs.forEach { it.webView.visibility = if (it.id == id) View.VISIBLE else View.GONE }
        showAddress(tab.url)
        refreshTabs()
        updateNavigationButtons()
    }

    private fun closeTab(id: Int) {
        val index = tabs.indexOfFirst { it.id == id }
        if (index < 0) return
        val wasCurrent = id == currentTabId
        val tab = tabs[index]
        tab.webView.stopLoading()
        webContainer.removeView(tab.webView)
        tab.webView.destroy()
        tabs.removeAt(index)
        if (tabs.isEmpty()) {
            currentTabId = -1
            createTab()
        } else if (wasCurrent) {
            switchTo(tabs[minOf(index, tabs.lastIndex)].id)
        } else {
            refreshTabs()
        }
    }

    private fun refreshTabs() {
        if (!::tabStrip.isInitialized) return
        tabStrip.removeAllViews()
        tabs.forEach { tab ->
            val chip = LinearLayout(this).apply {
                orientation = LinearLayout.HORIZONTAL
                gravity = Gravity.CENTER_VERTICAL
                background = rounded(
                    if (tab.id == currentTabId) C_ACCENT_DARK else C_PANEL,
                    if (tab.id == currentTabId) C_ACCENT else C_LINE,
                    11
                )
                setPadding(dp(10), 0, dp(4), 0)
            }
            val label = TextView(this).apply {
                text = tab.title.take(17)
                textSize = 11f
                maxLines = 1
                setTextColor(if (tab.id == currentTabId) C_TEXT else C_MUTED)
                typeface = Typeface.create("sans-serif", Typeface.BOLD)
                setPadding(0, dp(9), dp(5), dp(9))
                setOnClickListener { switchTo(tab.id) }
            }
            val close = TextView(this).apply {
                text = "×"
                textSize = 17f
                gravity = Gravity.CENTER
                setTextColor(C_MUTED)
                setPadding(dp(5), 0, dp(5), 0)
                setOnClickListener { closeTab(tab.id) }
            }
            chip.addView(label)
            chip.addView(close, LinearLayout.LayoutParams(dp(25), dp(34)))
            chip.setOnClickListener { switchTo(tab.id) }
            tabStrip.addView(chip, LinearLayout.LayoutParams(
                ViewGroup.LayoutParams.WRAP_CONTENT, dp(35)
            ).apply { marginEnd = dp(6) })
        }
    }

    private fun updateNavigationButtons() {
        val webView = currentTab()?.webView
        backButton.alpha = if (webView?.canGoBack() == true) 1f else 0.45f
        forwardButton.alpha = if (webView?.canGoForward() == true) 1f else 0.45f
    }

    private fun showAddress(value: String) {
        if (!::address.isInitialized) return
        val display = if (value == HOME_URL || value.startsWith("data:text/html")) "" else value
        address.setText(display, false)
    }

    private fun refreshSuggestions(query: String) {
        if (!::suggestionAdapter.isInitialized) return
        val normalized = query.lowercase()
        val urls = readEntries(KEY_HISTORY).asReversed().map { it.url } +
            readEntries(KEY_BOOKMARKS).map { it.url }
        val matches = urls.distinct()
            .filter { normalized.isBlank() || it.lowercase().contains(normalized) }
            .take(8)
        suggestionAdapter.clear()
        suggestionAdapter.addAll(matches)
        suggestionAdapter.notifyDataSetChanged()
    }

    private fun startDownload(
        url: String,
        userAgent: String,
        contentDisposition: String?,
        mimeType: String?
    ) {
        try {
            val uri = Uri.parse(url)
            if (uri.scheme != "https" && uri.scheme != "http") {
                toast("Этот тип загрузки не поддерживается")
                return
            }
            val filename = URLUtil.guessFileName(url, contentDisposition, mimeType)
                .replace(Regex("[\\\\/:*?\"<>|]"), "_")
            val request = DownloadManager.Request(uri)
                .setTitle(filename)
                .setDescription("Загрузка через NYX Browser")
                .setNotificationVisibility(DownloadManager.Request.VISIBILITY_VISIBLE_NOTIFY_COMPLETED)
                .setDestinationInExternalPublicDir(Environment.DIRECTORY_DOWNLOADS, filename)
            if (!mimeType.isNullOrBlank()) request.setMimeType(mimeType)
            if (userAgent.isNotBlank()) request.addRequestHeader("User-Agent", userAgent)
            CookieManager.getInstance().getCookie(url)?.let {
                request.addRequestHeader("Cookie", it)
            }
            val manager = getSystemService(DOWNLOAD_SERVICE) as DownloadManager
            manager.enqueue(request)
            toast("Загрузка началась: $filename")
        } catch (_: Exception) {
            toast("Не удалось начать загрузку")
        }
    }

    private fun openExternal(uri: Uri): Boolean {
        return try {
            startActivity(Intent(Intent.ACTION_VIEW, uri))
            true
        } catch (_: Exception) {
            toast("Нет приложения для открытия этой ссылки")
            true
        }
    }

    private fun saveEntry(key: String, entry: BrowserEntry, limit: Int) {
        val entries = readEntries(key)
        entries.removeAll { it.url == entry.url }
        entries.add(entry)
        while (entries.size > limit) entries.removeAt(0)
        val array = JSONArray()
        entries.forEach {
            array.put(JSONObject().put("title", it.title).put("url", it.url))
        }
        prefs.edit().putString(key, array.toString()).apply()
    }

    private fun readEntries(key: String): MutableList<BrowserEntry> {
        val raw = prefs.getString(key, "[]") ?: "[]"
        return try {
            val array = JSONArray(raw)
            MutableList(array.length()) { index ->
                val obj = array.getJSONObject(index)
                BrowserEntry(obj.optString("title", obj.optString("url")), obj.optString("url"))
            }.filter { it.url.startsWith("http://") || it.url.startsWith("https://") }.toMutableList()
        } catch (_: Exception) {
            mutableListOf()
        }
    }

    private fun showEntries(key: String, title: String) {
        val entries = readEntries(key).asReversed()
        if (entries.isEmpty()) {
            toast(if (key == KEY_BOOKMARKS) "Закладок пока нет" else "История пока пуста")
            return
        }
        AlertDialog.Builder(this)
            .setTitle(title)
            .setItems(entries.map { it.title.ifBlank { it.url }.take(45) }.toTypedArray()) { _, which ->
                currentTab()?.webView?.loadUrl(entries[which].url) ?: createTab(entries[which].url)
            }
            .setNegativeButton("Закрыть", null)
            .show()
    }

    private fun shareCurrentPage() {
        val tab = currentTab() ?: return
        if (!tab.url.startsWith("https://") && !tab.url.startsWith("http://")) {
            toast("На главной странице нечего отправлять")
            return
        }
        val intent = Intent(Intent.ACTION_SEND).apply {
            type = "text/plain"
            putExtra(Intent.EXTRA_TEXT, tab.url)
        }
        startActivity(Intent.createChooser(intent, "Поделиться страницей"))
    }

    private fun currentTab(): BrowserTab? = tabs.firstOrNull { it.id == currentTabId }
    private fun tabFor(webView: WebView): BrowserTab? = tabs.firstOrNull { it.webView === webView }

    private fun titleFor(url: String): String =
        Uri.parse(url).host?.removePrefix("www.") ?: "NYX"

    private fun button(text: String, width: Int, height: Int): TextView {
        return TextView(this).apply {
            this.text = text
            textSize = if (text.length > 3) 11f else 18f
            gravity = Gravity.CENTER
            setTextColor(C_TEXT)
            typeface = Typeface.create("sans-serif", Typeface.BOLD)
            background = rounded(C_PANEL, C_LINE, 12)
            isClickable = true
            isFocusable = true
            minWidth = if (width == 0) 0 else dp(width)
            setPadding(dp(6), dp(4), dp(6), dp(4))
            layoutParams = LinearLayout.LayoutParams(
                if (width == 0) 0 else dp(width), dp(height)
            )
        }
    }

    private fun rounded(fill: Int, stroke: Int, radius: Int): GradientDrawable {
        return GradientDrawable().apply {
            setColor(fill)
            setStroke(dp(1), stroke)
            cornerRadius = dp(radius).toFloat()
        }
    }

    private fun dp(value: Int): Int = (value * resources.displayMetrics.density).toInt()
    private fun toast(message: String) =
        Toast.makeText(this, message, Toast.LENGTH_SHORT).show()

    @Deprecated("Activity result API retained for compatibility with Android WebView file chooser")
    override fun onActivityResult(requestCode: Int, resultCode: Int, data: Intent?) {
        if (requestCode == FILE_CHOOSER_REQUEST) {
            val result = if (resultCode == RESULT_OK && data != null) {
                WebChromeClient.FileChooserParams.parseResult(resultCode, data)
            } else null
            pendingFileUpload?.onReceiveValue(result)
            pendingFileUpload = null
            return
        }
        super.onActivityResult(requestCode, resultCode, data)
    }

    override fun onBackPressed() {
        val webView = currentTab()?.webView
        if (webView?.canGoBack() == true) {
            webView.goBack()
        } else if (tabs.size > 1) {
            closeTab(currentTabId)
        } else {
            showHome()
        }
    }

    override fun onSaveInstanceState(outState: Bundle) {
        outState.putString(STATE_URL, currentTab()?.url)
        super.onSaveInstanceState(outState)
    }

    override fun onResume() {
        super.onResume()
        tabs.forEach {
            it.webView.onResume()
            it.webView.resumeTimers()
        }
    }

    override fun onPause() {
        tabs.forEach {
            it.webView.onPause()
            it.webView.pauseTimers()
        }
        super.onPause()
    }

    override fun onDestroy() {
        pendingFileUpload?.onReceiveValue(null)
        pendingFileUpload = null
        tabs.forEach {
            it.webView.stopLoading()
            it.webView.destroy()
        }
        tabs.clear()
        super.onDestroy()
    }

    private companion object {
        const val MAX_TABS = 12
        const val FILE_CHOOSER_REQUEST = 4102
        const val STATE_URL = "nyx.current.url"
        const val KEY_BOOKMARKS = "bookmarks"
        const val KEY_HISTORY = "history"
        const val HOME_URL = "https://nyx.local/"
        const val C_BG = Color.rgb(9, 8, 17)
        const val C_PANEL = Color.rgb(20, 18, 34)
        const val C_LINE = Color.rgb(48, 42, 64)
        const val C_TEXT = Color.rgb(245, 242, 255)
        const val C_MUTED = Color.rgb(162, 155, 182)
        const val C_ACCENT = Color.rgb(169, 139, 255)
        const val C_ACCENT_DARK = Color.rgb(47, 35, 76)

        val HOME_HTML = """
            <!doctype html><html lang="ru"><head>
            <meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
            <meta name="theme-color" content="#090811"><title>NYX</title>
            <style>
            *{box-sizing:border-box}body{margin:0;min-height:100vh;background:radial-gradient(ellipse at 50% 30%,#231a3b,#090811 65%);color:#f5f2ff;font:16px Arial,sans-serif;display:flex;align-items:center;justify-content:center;padding:22px}
            main{width:min(640px,100%);text-align:center}.logo{font-size:60px;font-weight:900;letter-spacing:-5px}.logo span{color:#a98bff}p{color:#a29bb6;line-height:1.7}.search{display:flex;gap:8px;margin:28px 0}.search input{min-width:0;flex:1;padding:15px;border:1px solid #302a40;border-radius:13px;background:#141222;color:white;font-size:16px}.search button{border:0;border-radius:13px;padding:0 18px;background:#a98bff;color:#160e2b;font-weight:800;font-size:15px}
            .links{display:grid;grid-template-columns:repeat(3,1fr);gap:10px;margin-top:24px}.links a{padding:16px 8px;border:1px solid #302a40;border-radius:13px;background:#141222;color:#dcd1ff;text-decoration:none;font-weight:700}.links a:active{background:#2f234c}
            small{display:block;margin-top:30px;color:#726b84;line-height:1.6}@media(max-width:420px){.logo{font-size:50px}.links{grid-template-columns:repeat(2,1fr)}.search input{font-size:14px}}
            </style></head><body><main><div class="logo">N<span>YX</span></div><p>Твой интернет. Твои правила.</p>
            <form class="search" action="https://www.google.com/search" method="get"><input name="q" placeholder="Поиск в интернете..." autocomplete="off"><button type="submit">Найти</button></form>
            <div class="links"><a href="https://www.youtube.com">YouTube</a><a href="https://github.com">GitHub</a><a href="https://wikipedia.org">Wikipedia</a></div>
            <small>NYX Browser для Android · Бесплатно · Без встроенной рекламы</small></main></body></html>
        """.trimIndent()
    }
}

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
import android.os.Bundle
import android.os.Environment
import android.view.Gravity
import android.view.View
import android.view.ViewGroup
import android.view.inputmethod.EditorInfo
import android.webkit.CookieManager
import android.webkit.DownloadListener
import android.webkit.ValueCallback
import android.webkit.WebChromeClient
import android.webkit.WebResourceRequest
import android.webkit.WebView
import android.webkit.WebViewClient
import android.webkit.URLUtil
import android.widget.EditText
import android.widget.FrameLayout
import android.widget.LinearLayout
import android.widget.ProgressBar
import android.widget.TextView
import android.widget.Toast
import org.json.JSONArray

private const val HOME_TOKEN = "NYX_HOME"
private const val HOME_BASE_URL = "https://nyx.local/"

class MainActivity : Activity() {
    private data class BrowserTab(
        val id: Int,
        val webView: WebView,
        var title: String = "Новая вкладка",
        var isHome: Boolean = true
    )

    private val tabs = mutableListOf<BrowserTab>()
    private var activeTab: BrowserTab? = null
    private var nextTabId = 1
    private lateinit var addressBar: EditText
    private lateinit var progress: ProgressBar
    private lateinit var webHost: FrameLayout
    private lateinit var tabButton: TextView
    private var fileChooserCallback: ValueCallback<Array<Uri>>? = null
    private val prefs by lazy { getSharedPreferences("nyx-browser", Context.MODE_PRIVATE) }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        window.statusBarColor = Color.rgb(9, 8, 17)
        window.navigationBarColor = Color.rgb(9, 8, 17)
        window.setSoftInputMode(android.view.WindowManager.LayoutParams.SOFT_INPUT_ADJUST_RESIZE)
        buildInterface()
        WebView.setWebContentsDebuggingEnabled(BuildConfig.DEBUG)
        WebView.startSafeBrowsing(this) { }
        restoreSession()
    }

    private fun buildInterface() {
        val root = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            setBackgroundColor(Color.rgb(9, 8, 17))
        }
        val toolbar = LinearLayout(this).apply {
            orientation = LinearLayout.HORIZONTAL
            gravity = Gravity.CENTER_VERTICAL
            setPadding(dp(6), dp(8), dp(6), dp(6))
            setBackgroundColor(Color.rgb(20, 18, 34))
        }
        val backButton = actionButton("‹") { activeTab?.webView?.let { if (it.canGoBack()) it.goBack() } }
        val forwardButton = actionButton("›") { activeTab?.webView?.let { if (it.canGoForward()) it.goForward() } }
        val reloadButton = actionButton("↻") { activeTab?.webView?.reload() }

        addressBar = EditText(this).apply {
            setSingleLine(true)
            setTextColor(Color.WHITE)
            setHintTextColor(Color.rgb(162, 155, 182))
            hint = "Поиск или адрес сайта"
            textSize = 14f
            imeOptions = EditorInfo.IME_ACTION_GO
            setPadding(dp(12), 0, dp(8), 0)
            background = rounded(Color.rgb(35, 30, 53), Color.rgb(65, 55, 91), 13)
            setSelectAllOnFocus(true)
            setOnEditorActionListener { _, actionId, _ ->
                if (actionId == EditorInfo.IME_ACTION_GO || actionId == EditorInfo.IME_ACTION_SEARCH) {
                    navigateFromAddress()
                    true
                } else false
            }
        }
        val goButton = actionButton("GO") { navigateFromAddress() }.apply {
            textSize = 11f
            setTextColor(Color.rgb(22, 14, 43))
            background = rounded(Color.rgb(169, 139, 255), Color.rgb(169, 139, 255), 12)
        }

        toolbar.addView(backButton, LinearLayout.LayoutParams(dp(34), dp(42)))
        toolbar.addView(forwardButton, LinearLayout.LayoutParams(dp(34), dp(42)))
        toolbar.addView(reloadButton, LinearLayout.LayoutParams(dp(34), dp(42)))
        toolbar.addView(addressBar, LinearLayout.LayoutParams(0, dp(42), 1f).apply {
            leftMargin = dp(4)
            rightMargin = dp(4)
        })
        toolbar.addView(goButton, LinearLayout.LayoutParams(dp(44), dp(42)))

        progress = ProgressBar(this, null, android.R.attr.progressBarStyleHorizontal).apply {
            max = 100
            progressTintList = android.content.res.ColorStateList.valueOf(Color.rgb(169, 139, 255))
            progressBackgroundTintList = android.content.res.ColorStateList.valueOf(Color.rgb(35, 30, 53))
            visibility = View.GONE
        }
        webHost = FrameLayout(this).apply { setBackgroundColor(Color.rgb(9, 8, 17)) }

        val bottom = LinearLayout(this).apply {
            orientation = LinearLayout.HORIZONTAL
            gravity = Gravity.CENTER
            setPadding(dp(8), dp(5), dp(8), dp(7))
            setBackgroundColor(Color.rgb(20, 18, 34))
        }
        bottom.addView(actionButton("⌂  Домой") { activeTab?.let { loadHome(it) } }, weightParams())
        bottom.addView(actionButton("＋  Вкладка") { createTab() }, weightParams())
        tabButton = actionButton("▢  1") { showTabs() }
        bottom.addView(tabButton, weightParams())

        root.addView(toolbar, LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, dp(56)))
        root.addView(progress, LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, dp(3)))
        root.addView(webHost, LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, 0, 1f))
        root.addView(bottom, LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, dp(54)))
        setContentView(root)
    }

    private fun actionButton(label: String, action: () -> Unit): TextView =
        TextView(this).apply {
            text = label
            textSize = 16f
            gravity = Gravity.CENTER
            setTextColor(Color.rgb(235, 228, 255))
            typeface = Typeface.DEFAULT_BOLD
            background = rounded(Color.rgb(35, 30, 53), Color.rgb(65, 55, 91), 11)
            isClickable = true
            isFocusable = true
            setOnClickListener { action() }
            setPadding(dp(4), 0, dp(4), 0)
        }

    private fun rounded(fill: Int, stroke: Int, radius: Int): GradientDrawable =
        GradientDrawable().apply {
            setColor(fill)
            setCornerRadius(dp(radius).toFloat())
            setStroke(dp(1), stroke)
        }

    private fun weightParams() = LinearLayout.LayoutParams(0, dp(42), 1f).apply {
        leftMargin = dp(4)
        rightMargin = dp(4)
    }

    private fun dp(value: Int): Int = (value * resources.displayMetrics.density).toInt()

    private fun createTab(initialUrl: String? = null) {
        val webView = WebView(this)
        webView.setBackgroundColor(Color.rgb(9, 8, 17))
        webView.settings.apply {
            javaScriptEnabled = true
            domStorageEnabled = true
            databaseEnabled = true
            javaScriptCanOpenWindowsAutomatically = false
            setSupportMultipleWindows(false)
            allowFileAccess = false
            allowContentAccess = true
            loadsImagesAutomatically = true
            useWideViewPort = true
            loadWithOverviewMode = true
            setSupportZoom(true)
            builtInZoomControls = true
            displayZoomControls = false
            mediaPlaybackRequiresUserGesture = true
            mixedContentMode = android.webkit.WebSettings.MIXED_CONTENT_NEVER_ALLOW
            safeBrowsingEnabled = true
        }
        CookieManager.getInstance().setAcceptCookie(true)
        CookieManager.getInstance().setAcceptThirdPartyCookies(webView, true)

        val tab = BrowserTab(nextTabId++, webView)
        webView.webViewClient = object : WebViewClient() {
            override fun shouldOverrideUrlLoading(view: WebView, request: WebResourceRequest): Boolean {
                val uri = request.url
                if (uri.scheme == "http" || uri.scheme == "https") return false
                return try {
                    startActivity(Intent(Intent.ACTION_VIEW, uri))
                    true
                } catch (_: Exception) {
                    Toast.makeText(this@MainActivity, "Не удалось открыть эту ссылку", Toast.LENGTH_SHORT).show()
                    true
                }
            }

            override fun onPageStarted(view: WebView, url: String?, favicon: android.graphics.Bitmap?) {
                tab.isHome = false
                if (activeTab == tab) {
                    progress.visibility = View.VISIBLE
                    addressBar.setText(url.orEmpty())
                }
            }

            override fun onPageFinished(view: WebView, url: String?) {
                if (activeTab == tab) {
                    progress.visibility = View.GONE
                    updateToolbar()
                }
                saveSession()
            }
        }

        webView.webChromeClient = object : WebChromeClient() {
            override fun onProgressChanged(view: WebView, newProgress: Int) {
                if (activeTab == tab) {
                    progress.progress = newProgress
                    progress.visibility = if (newProgress in 1..99) View.VISIBLE else View.GONE
                }
            }

            override fun onReceivedTitle(view: WebView, title: String?) {
                tab.title = title?.take(80).orEmpty().ifBlank { "Страница" }
                if (activeTab == tab) updateTabCount()
            }

            override fun onShowFileChooser(
                view: WebView,
                callback: ValueCallback<Array<Uri>>,
                params: FileChooserParams
            ): Boolean {
                fileChooserCallback?.onReceiveValue(null)
                fileChooserCallback = callback
                return try {
                    startActivityForResult(params.createIntent(), FILE_CHOOSER_REQUEST)
                    true
                } catch (_: Exception) {
                    fileChooserCallback = null
                    callback.onReceiveValue(null)
                    false
                }
            }

            override fun onPermissionRequest(request: android.webkit.PermissionRequest) {
                request.deny()
            }

            override fun onGeolocationPermissionsShowPrompt(
                origin: String,
                callback: android.webkit.GeolocationPermissions.Callback
            ) {
                callback.invoke(origin, false, false)
            }
        }

        webView.setDownloadListener(DownloadListener { url, userAgent, contentDisposition, mimeType, _ ->
            enqueueDownload(url, userAgent, contentDisposition, mimeType)
        })
        webHost.addView(
            webView,
            FrameLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.MATCH_PARENT)
        )
        tabs.add(tab)
        switchTo(tab)

        if (initialUrl.isNullOrBlank()) loadHome(tab) else {
            tab.isHome = false
            webView.loadUrl(initialUrl)
        }
        updateTabCount()
    }

    private fun loadHome(tab: BrowserTab) {
        tab.isHome = true
        val html = assets.open("home.html").bufferedReader(Charsets.UTF_8).use { it.readText() }
        tab.webView.loadDataWithBaseURL(HOME_BASE_URL, html, "text/html", "UTF-8", null)
        if (activeTab == tab) addressBar.setText("NYX Home")
        saveSession()
    }

    private fun navigateFromAddress() {
        val input = addressBar.text.toString().trim()
        if (input.isEmpty()) return
        val tab = activeTab ?: return
        tab.isHome = false
        tab.webView.loadUrl(resolveAddress(input))
        addressBar.clearFocus()
    }

    private fun resolveAddress(input: String): String {
        if (input.any { it.isWhitespace() }) {
            return "https://www.google.com/search?q=" + Uri.encode(input)
        }
        val candidate = if (input.matches(Regex("^[a-zA-Z][a-zA-Z0-9+.-]*:.*"))) {
            input
        } else {
            "https://$input"
        }
        val parsed = Uri.parse(candidate)
        return if (parsed.host.isNullOrBlank()) {
            "https://www.google.com/search?q=" + Uri.encode(input)
        } else candidate
    }

    private fun switchTo(tab: BrowserTab) {
        activeTab = tab
        tabs.forEach { it.webView.visibility = if (it == tab) View.VISIBLE else View.GONE }
        addressBar.setText(if (tab.isHome) "NYX Home" else tab.webView.url.orEmpty())
        updateToolbar()
        updateTabCount()
    }

    private fun updateToolbar() {
        val tab = activeTab ?: return
        if (!addressBar.hasFocus()) {
            addressBar.setText(if (tab.isHome) "NYX Home" else tab.webView.url.orEmpty())
        }
        tabButton.text = "▢  " + tabs.size
    }

    private fun updateTabCount() {
        if (::tabButton.isInitialized) tabButton.text = "▢  " + tabs.size
    }

    private fun showTabs() {
        if (tabs.isEmpty()) return
        val labels = tabs.mapIndexed { index, tab ->
            (if (tab == activeTab) "● " else "") + (index + 1) + ". " + tab.title
        }.toTypedArray()
        AlertDialog.Builder(this)
            .setTitle("Вкладки")
            .setItems(labels) { _, which -> switchTo(tabs[which]) }
            .setPositiveButton("Новая вкладка") { _, _ -> createTab() }
            .setNegativeButton("Закрыть текущую") { _, _ -> activeTab?.let { closeTab(it) } }
            .show()
    }

    private fun closeTab(tab: BrowserTab) {
        val index = tabs.indexOf(tab)
        if (index < 0) return
        tabs.removeAt(index)
        webHost.removeView(tab.webView)
        tab.webView.stopLoading()
        tab.webView.loadUrl("about:blank")
        tab.webView.destroy()
        if (tabs.isEmpty()) createTab() else switchTo(tabs[index.coerceAtMost(tabs.lastIndex)])
        saveSession()
    }

    private fun enqueueDownload(url: String, userAgent: String?, contentDisposition: String?, mimeType: String?) {
        try {
            val request = DownloadManager.Request(Uri.parse(url))
                .setNotificationVisibility(DownloadManager.Request.VISIBILITY_VISIBLE_NOTIFY_COMPLETED)
                .setAllowedOverMetered(true)
                .setAllowedOverRoaming(false)
                .setDestinationInExternalPublicDir(
                    Environment.DIRECTORY_DOWNLOADS,
                    URLUtil.guessFileName(url, contentDisposition, mimeType)
                )
            if (!mimeType.isNullOrBlank()) request.setMimeType(mimeType)
            if (!userAgent.isNullOrBlank()) request.addRequestHeader("User-Agent", userAgent)
            CookieManager.getInstance().getCookie(url)?.let { request.addRequestHeader("Cookie", it) }
            (getSystemService(DOWNLOAD_SERVICE) as DownloadManager).enqueue(request)
            Toast.makeText(this, "Загрузка добавлена", Toast.LENGTH_SHORT).show()
        } catch (error: Exception) {
            Toast.makeText(this, "Не удалось начать загрузку: " + error.message, Toast.LENGTH_LONG).show()
        }
    }

    private fun restoreSession() {
        val restored = mutableListOf<String>()
        try {
            val array = JSONArray(prefs.getString("tabs", "[]"))
            for (index in 0 until array.length()) restored.add(array.optString(index))
        } catch (_: Exception) { }
        if (restored.isEmpty()) {
            createTab()
            return
        }
        restored.take(MAX_RESTORED_TABS).forEach { value ->
            if (value == HOME_TOKEN) createTab() else createTab(value)
        }
    }

    private fun saveSession() {
        if (tabs.isEmpty()) return
        val values = JSONArray()
        tabs.take(MAX_RESTORED_TABS).forEach { tab ->
            val value = if (tab.isHome) HOME_TOKEN else tab.webView.url.orEmpty()
            if (value.isNotBlank()) values.put(value)
        }
        prefs.edit().putString("tabs", values.toString()).apply()
    }

    override fun onActivityResult(requestCode: Int, resultCode: Int, data: Intent?) {
        super.onActivityResult(requestCode, resultCode, data)
        if (requestCode == FILE_CHOOSER_REQUEST) {
            val callback = fileChooserCallback ?: return
            fileChooserCallback = null
            callback.onReceiveValue(FileChooserParams.parseResult(resultCode, data))
        }
    }

    override fun onBackPressed() {
        val tab = activeTab
        when {
            tab?.webView?.canGoBack() == true -> tab.webView.goBack()
            tabs.size > 1 && tab != null -> closeTab(tab)
            else -> super.onBackPressed()
        }
    }

    override fun onPause() {
        tabs.forEach { it.webView.onPause() }
        saveSession()
        super.onPause()
    }

    override fun onResume() {
        super.onResume()
        tabs.forEach { it.webView.onResume() }
    }

    override fun onDestroy() {
        tabs.forEach {
            it.webView.stopLoading()
            it.webView.destroy()
        }
        tabs.clear()
        super.onDestroy()
    }

    companion object {
        private const val FILE_CHOOSER_REQUEST = 4102
        private const val MAX_RESTORED_TABS = 8
    }
}

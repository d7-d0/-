from flask import Flask, render_template_string, request, redirect, jsonify
import discord
from discord.ext import commands
import threading
import asyncio
from datetime import datetime
import aiohttp

app = Flask(__name__)

# ===== تخزين البيانات المركزي =====
bots = {}

# ===== واجهة المستخدم الاحترافية (HTML + CSS + JS) =====
HTML = """
<!doctype html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Discord Master Dashboard ⚡</title>
    <link href="https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;900&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg-deep:    #0d0e10;
            --bg-card:    #161920;
            --bg-panel:   #1e2229;
            --bg-input:   #252b34;
            --accent:     #5865f2;
            --accent-glow:#5865f240;
            --green:      #23d18b;
            --red:        #ed4245;
            --yellow:     #faa61a;
            --text:       #e8eaf0;
            --muted:      #72767d;
            --border:     #2a2d36;
            --online:     #23d18b;
            --idle:       #faa61a;
            --dnd:        #ed4245;
            --offline:    #4f545c;
        }

        * { box-sizing: border-box; margin: 0; padding: 0; }

        body {
            font-family: 'Cairo', sans-serif;
            background: var(--bg-deep);
            color: var(--text);
            min-height: 100vh;
            overflow-x: hidden;
        }

        /* خلفية متحركة */
        body::before {
            content: '';
            position: fixed; inset: 0; z-index: -1;
            background:
                radial-gradient(ellipse 60% 40% at 20% 10%, #5865f215 0%, transparent 60%),
                radial-gradient(ellipse 50% 60% at 80% 80%, #23d18b0a 0%, transparent 60%);
            animation: bgPulse 10s ease-in-out infinite alternate;
        }

        @keyframes bgPulse {
            0%   { opacity: 0.6; }
            100% { opacity: 1; }
        }

        /* هيدر */
        .header {
            background: linear-gradient(90deg, #0d0e10 0%, #1a1c2e 50%, #0d0e10 100%);
            border-bottom: 1px solid var(--border);
            padding: 18px 30px;
            display: flex; align-items: center; justify-content: space-between;
            position: sticky; top: 0; z-index: 100;
            backdrop-filter: blur(10px);
        }

        .header-logo {
            display: flex; align-items: center; gap: 12px;
        }

        .header-logo .icon {
            width: 42px; height: 42px; background: var(--accent);
            border-radius: 12px; display: flex; align-items: center; justify-content: center;
            font-size: 22px; box-shadow: 0 0 20px var(--accent-glow);
            animation: iconPulse 3s ease-in-out infinite;
        }

        @keyframes iconPulse {
            0%, 100% { box-shadow: 0 0 20px var(--accent-glow); }
            50% { box-shadow: 0 0 35px #5865f260; }
        }

        .header-title { font-size: 1.3rem; font-weight: 900; }
        .header-title span { color: var(--accent); }

        .header-stats { display: flex; gap: 20px; }
        .stat-chip {
            background: var(--bg-panel);
            border: 1px solid var(--border);
            border-radius: 20px;
            padding: 6px 14px;
            font-size: 0.8rem;
            display: flex; align-items: center; gap: 6px;
        }
        .stat-chip .dot { width: 8px; height: 8px; border-radius: 50%; background: var(--green); animation: blink 2s infinite; }
        @keyframes blink { 0%,100%{opacity:1} 50%{opacity:0.3} }

        /* المحتوى الرئيسي */
        .container { max-width: 1500px; margin: auto; padding: 25px; }

        /* بطاقة إضافة البوت */
        .add-bot-card {
            background: var(--bg-card);
            border: 1px solid var(--border);
            border-top: 3px solid var(--accent);
            border-radius: 16px;
            padding: 24px;
            margin-bottom: 30px;
            position: relative;
            overflow: hidden;
        }

        .add-bot-card::after {
            content: '🔌';
            position: absolute; right: 25px; top: 50%; transform: translateY(-50%);
            font-size: 80px; opacity: 0.05;
        }

        .add-bot-card h3 { font-size: 1.1rem; color: var(--accent); margin-bottom: 15px; }
        .add-form { display: flex; gap: 12px; align-items: flex-end; flex-wrap: wrap; }
        .form-group { display: flex; flex-direction: column; gap: 6px; }
        .form-group label { font-size: 0.78rem; color: var(--muted); font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; }

        input, select, textarea {
            background: var(--bg-input);
            border: 1px solid var(--border);
            border-radius: 8px;
            color: var(--text);
            padding: 10px 14px;
            font-family: 'Cairo', sans-serif;
            font-size: 0.9rem;
            transition: border-color 0.2s, box-shadow 0.2s;
            outline: none;
        }

        input:focus, select:focus, textarea:focus {
            border-color: var(--accent);
            box-shadow: 0 0 0 3px var(--accent-glow);
        }

        button {
            border: none; cursor: pointer;
            border-radius: 8px; padding: 10px 20px;
            font-family: 'Cairo', sans-serif; font-weight: 700;
            font-size: 0.9rem; transition: all 0.2s; white-space: nowrap;
        }

        .btn-primary { background: var(--accent); color: white; }
        .btn-primary:hover { background: #4752c4; transform: translateY(-1px); box-shadow: 0 4px 15px var(--accent-glow); }

        .btn-success { background: var(--green); color: #0d0e10; }
        .btn-success:hover { filter: brightness(1.1); transform: translateY(-1px); }

        .btn-danger { background: var(--red); color: white; padding: 7px 14px; font-size: 0.8rem; }
        .btn-danger:hover { filter: brightness(1.1); }

        .btn-warn { background: var(--yellow); color: #0d0e10; padding: 7px 14px; font-size: 0.8rem; }

        .btn-ghost {
            background: transparent; border: 1px solid var(--border);
            color: var(--text); padding: 7px 14px; font-size: 0.8rem;
        }
        .btn-ghost:hover { border-color: var(--accent); color: var(--accent); }

        /* بطاقة البوت الرئيسية */
        .bot-card {
            background: var(--bg-card);
            border: 1px solid var(--border);
            border-radius: 16px;
            margin-bottom: 30px;
            overflow: hidden;
            animation: slideIn 0.4s ease-out;
        }

        @keyframes slideIn {
            from { opacity: 0; transform: translateY(20px); }
            to   { opacity: 1; transform: translateY(0); }
        }

        .bot-header {
            background: linear-gradient(135deg, #1a1c2e 0%, #1e2229 100%);
            border-bottom: 1px solid var(--border);
            padding: 16px 20px;
            display: flex; align-items: center; justify-content: space-between;
        }

        .bot-info { display: flex; align-items: center; gap: 14px; }

        .bot-avatar {
            width: 46px; height: 46px; border-radius: 50%;
            background: var(--accent); display: flex; align-items: center; justify-content: center;
            font-size: 22px; border: 2px solid var(--accent);
            box-shadow: 0 0 15px var(--accent-glow);
        }

        .bot-name { font-size: 1.1rem; font-weight: 900; }
        .bot-status { font-size: 0.8rem; color: var(--green); display: flex; align-items: center; gap: 5px; }
        .bot-status::before { content: ''; width: 7px; height: 7px; border-radius: 50%; background: var(--green); animation: blink 2s infinite; display: inline-block; }

        /* شبكة التخطيط الرئيسية */
        .bot-body { padding: 20px; }
        .main-grid {
            display: grid;
            grid-template-columns: 240px 1fr 280px;
            gap: 16px;
            height: 580px;
        }

        /* الأعمدة */
        .col {
            background: var(--bg-panel);
            border-radius: 12px;
            border: 1px solid var(--border);
            display: flex; flex-direction: column;
            overflow: hidden;
        }

        .col-header {
            padding: 12px 15px;
            border-bottom: 1px solid var(--border);
            font-size: 0.82rem; font-weight: 700;
            color: var(--muted); text-transform: uppercase; letter-spacing: 0.8px;
            display: flex; align-items: center; gap: 8px;
        }

        .col-header .count {
            background: var(--bg-input); border-radius: 10px;
            padding: 2px 8px; font-size: 0.75rem; color: var(--text);
        }

        .col-body { flex: 1; overflow-y: auto; padding: 10px; }
        .col-footer { padding: 10px; border-top: 1px solid var(--border); }

        /* تمرير مخصص */
        .col-body::-webkit-scrollbar { width: 4px; }
        .col-body::-webkit-scrollbar-track { background: transparent; }
        .col-body::-webkit-scrollbar-thumb { background: var(--border); border-radius: 2px; }

        /* القنوات */
        .channel-item {
            display: flex; align-items: center; justify-content: space-between;
            padding: 7px 10px; border-radius: 6px; cursor: pointer;
            transition: background 0.15s; margin-bottom: 2px;
            font-size: 0.88rem;
        }
        .channel-item:hover { background: var(--bg-input); }

        .channel-item .ch-name { display: flex; align-items: center; gap: 6px; color: var(--muted); }
        .channel-item:hover .ch-name { color: var(--text); }

        .channel-item .ch-name span.prefix { color: var(--muted); font-weight: 900; }

        /* الرسائل */
        .message {
            display: flex; gap: 10px; padding: 8px; border-radius: 8px;
            margin-bottom: 4px; transition: background 0.15s; position: relative;
        }
        .message:hover { background: var(--bg-input); }
        .message.msg-deleted {
            background: rgba(237, 66, 69, 0.07);
            border-right: 2px solid var(--red);
        }
        .message.msg-bot {
            border-right: 2px solid var(--accent);
        }

        .msg-avatar {
            width: 36px; height: 36px; border-radius: 50%;
            object-fit: cover; flex-shrink: 0;
            border: 2px solid var(--border);
        }

        .msg-content-wrap { flex: 1; min-width: 0; }
        .msg-meta { display: flex; align-items: center; gap: 8px; margin-bottom: 2px; }
        .msg-author { font-weight: 700; font-size: 0.88rem; }
        .msg-time { color: var(--muted); font-size: 0.72rem; }
        .bot-tag {
            background: var(--accent); color: white;
            font-size: 0.65rem; padding: 1px 5px; border-radius: 3px; font-weight: 700;
        }
        .del-tag {
            color: var(--red); font-size: 0.7rem; font-weight: 700;
        }
        .msg-text { color: #b9bbbe; font-size: 0.87rem; word-break: break-word; line-height: 1.5; }
        .msg-img { max-width: 200px; border-radius: 6px; margin-top: 5px; cursor: pointer; display: block; border: 1px solid var(--border); }

        /* الأعضاء */
        .member-item {
            display: flex; align-items: center; gap: 8px;
            padding: 6px 8px; border-radius: 6px;
            margin-bottom: 2px; transition: background 0.15s;
            font-size: 0.85rem;
        }
        .member-item:hover { background: var(--bg-input); }

        .status-dot {
            width: 9px; height: 9px; border-radius: 50%; flex-shrink: 0;
        }
        .status-dot.online  { background: var(--online); }
        .status-dot.idle    { background: var(--idle); }
        .status-dot.dnd     { background: var(--dnd); }
        .status-dot.offline { background: var(--offline); }

        .member-name { flex: 1; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
        .member-guild { color: var(--muted); font-size: 0.72rem; }

        .member-actions { display: flex; gap: 4px; opacity: 0; transition: opacity 0.2s; }
        .member-item:hover .member-actions { opacity: 1; }

        /* عمود الإعدادات */
        .settings-section { padding: 12px; border-bottom: 1px solid var(--border); }
        .settings-section:last-child { border-bottom: none; }
        .settings-title { font-size: 0.78rem; color: var(--muted); font-weight: 700; text-transform: uppercase; letter-spacing: 0.6px; margin-bottom: 8px; }

        /* رسالة "لا يوجد" */
        .empty-state {
            display: flex; flex-direction: column; align-items: center; justify-content: center;
            height: 100%; color: var(--muted); text-align: center; padding: 20px;
        }
        .empty-state .emoji { font-size: 40px; margin-bottom: 10px; }

        /* حالة إضافة بوت أولى */
        .welcome-card {
            background: var(--bg-card);
            border: 1px dashed var(--border);
            border-radius: 16px;
            padding: 60px;
            text-align: center;
            animation: fadeIn 0.5s ease-out;
        }
        @keyframes fadeIn { from{opacity:0} to{opacity:1} }

        .welcome-card h2 { color: var(--accent); font-size: 1.8rem; margin-bottom: 12px; }
        .welcome-card p { color: var(--muted); margin-bottom: 30px; font-size: 0.95rem; }
        .welcome-form { display: flex; flex-direction: column; gap: 12px; max-width: 420px; margin: auto; }
        .welcome-form input { padding: 13px 16px; font-size: 1rem; }

        /* تبويبات البوت */
        .bot-tabs { display: flex; gap: 2px; padding: 0 20px; border-bottom: 1px solid var(--border); background: var(--bg-card); }
        .bot-tab {
            padding: 10px 16px; cursor: pointer; font-size: 0.85rem; font-weight: 600;
            color: var(--muted); border-bottom: 2px solid transparent;
            transition: all 0.2s; font-family: 'Cairo', sans-serif;
        }
        .bot-tab.active { color: var(--accent); border-bottom-color: var(--accent); }
        .bot-tab:hover { color: var(--text); }

        .tab-content { display: none; }
        .tab-content.active { display: block; }

        /* Identity panel */
        .identity-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 15px; padding: 20px; }
        .identity-form-group { display: flex; flex-direction: column; gap: 6px; }
        .identity-form-group label { font-size: 0.78rem; color: var(--muted); font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px; }
        .identity-form-group input, .identity-form-group textarea { width: 100%; }
        .identity-form-group textarea { height: 70px; resize: none; }

        /* إشعارات */
        .toast {
            position: fixed; bottom: 24px; left: 50%; transform: translateX(-50%) translateY(80px);
            background: var(--bg-panel); border: 1px solid var(--border);
            border-radius: 10px; padding: 12px 20px; font-size: 0.9rem;
            box-shadow: 0 8px 30px rgba(0,0,0,0.5);
            transition: transform 0.3s; z-index: 9999; display: flex; align-items: center; gap: 10px;
        }
        .toast.show { transform: translateX(-50%) translateY(0); }
        .toast.success { border-top: 2px solid var(--green); }
        .toast.error { border-top: 2px solid var(--red); }

        /* Responsive */
        @media (max-width: 1100px) {
            .main-grid { grid-template-columns: 1fr 1fr; height: auto; }
            .main-grid .col:first-child { display: none; }
        }
        @media (max-width: 750px) {
            .main-grid { grid-template-columns: 1fr; }
            .add-form { flex-direction: column; }
        }
    </style>
</head>
<body>

<!-- هيدر -->
<div class="header">
    <div class="header-logo">
        <div class="icon">⚡</div>
        <div>
            <div class="header-title">Discord <span>Master</span> Dashboard</div>
        </div>
    </div>
    <div class="header-stats">
        <div class="stat-chip">
            <div class="dot"></div>
            <span id="total-bots">{{ bots|length }} بوت متصل</span>
        </div>
        <div class="stat-chip">🕐 <span id="clock"></span></div>
    </div>
</div>

<!-- الإشعار -->
<div class="toast" id="toast">
    <span id="toast-icon">✅</span>
    <span id="toast-msg">تمت العملية بنجاح</span>
</div>

<div class="container">

    <!-- بطاقة إضافة بوت -->
    <div class="add-bot-card">
        <h3>🔌 ربط بوت ديسكورد جديد</h3>
        <form method="POST" action="/add_bot">
            <div class="add-form">
                <div class="form-group">
                    <label>اسم البوت</label>
                    <input type="text" name="bot_name" placeholder="مثال: بوت المتجر" required style="width: 180px;">
                </div>
                <div class="form-group">
                    <label>توكن البوت (Bot Token)</label>
                    <input type="password" name="bot_token" placeholder="أدخل التوكن السري هنا..." required style="width: 380px;">
                </div>
                <div class="form-group">
                    <label>&nbsp;</label>
                    <button type="submit" class="btn-primary">⚡ تشغيل البوت</button>
                </div>
            </div>
        </form>
    </div>

    <!-- بطاقات البوتات -->
    {% if bots %}
        {% for name, info in bots.items() %}
        <div class="bot-card" id="card-{{ name }}">
            <!-- هيدر البوت -->
            <div class="bot-header">
                <div class="bot-info">
                    <div class="bot-avatar">🤖</div>
                    <div>
                        <div class="bot-name">{{ name }}</div>
                        <div class="bot-status">متصل الآن</div>
                    </div>
                </div>
                <div style="display:flex; gap:8px;">
                    <span style="color: var(--muted); font-size: 0.8rem; padding: 6px 12px; background: var(--bg-input); border-radius: 20px;">
                        🌐 ديسكورد
                    </span>
                    <form action="/remove_bot/{{ name }}" method="POST" style="display:inline;">
                        <button type="submit" class="btn-danger">🗑️ إزالة البوت</button>
                    </form>
                </div>
            </div>

            <!-- التبويبات -->
            <div class="bot-tabs">
                <div class="bot-tab active" onclick="switchTab('{{ name }}', 'monitor')">📡 المراقبة</div>
                <div class="bot-tab" onclick="switchTab('{{ name }}', 'identity')">🎨 الهوية</div>
                <div class="bot-tab" onclick="switchTab('{{ name }}', 'actions')">⚙️ الإجراءات</div>
            </div>

            <!-- تبويب المراقبة -->
            <div class="tab-content active" id="tab-{{ name }}-monitor">
                <div class="bot-body">
                    <div class="main-grid">

                        <!-- عمود القنوات -->
                        <div class="col">
                            <div class="col-header">
                                📁 القنوات
                                <span class="count" id="chan-count-{{ name }}">0</span>
                            </div>
                            <div class="col-body" id="channels-{{ name }}">
                                <div class="empty-state"><div class="emoji">📡</div>جارٍ الجلب...</div>
                            </div>
                            <div class="col-footer">
                                <input type="text" id="new-ch-{{ name }}" placeholder="اسم القناة الجديدة..." style="width:100%; margin-bottom:6px;">
                                <div style="display:flex; gap:6px;">
                                    <button class="btn-primary" style="flex:1; padding:8px;" onclick="createChannel('{{ name }}', 'text')">+ نصية</button>
                                    <button class="btn-success" style="flex:1; padding:8px;" onclick="createChannel('{{ name }}', 'voice')">+ صوتية</button>
                                </div>
                            </div>
                        </div>

                        <!-- عمود الرسائل -->
                        <div class="col">
                            <div class="col-header">
                                💬 الرسائل المباشرة
                                <span class="count" id="msg-count-{{ name }}">0</span>
                            </div>
                            <div class="col-body" id="messages-{{ name }}">
                                <div class="empty-state"><div class="emoji">💬</div>جارٍ جلب المحادثات...</div>
                            </div>
                            <div class="col-footer">
                                <div style="display:flex; gap:6px; margin-bottom:6px;">
                                    <input type="text" id="dm-id-{{ name }}" placeholder="معرّف المستخدم (User ID)" style="flex:1;">
                                </div>
                                <div style="display:flex; gap:6px;">
                                    <input type="text" id="dm-msg-{{ name }}" placeholder="رسالة خاصة..." style="flex:1;">
                                    <button class="btn-primary" onclick="sendDM('{{ name }}')">إرسال ✉️</button>
                                </div>
                            </div>
                        </div>

                        <!-- عمود الأعضاء -->
                        <div class="col">
                            <div class="col-header">
                                👥 الأعضاء
                                <span class="count" id="mem-count-{{ name }}">0</span>
                            </div>
                            <div class="col-body" id="members-{{ name }}">
                                <div class="empty-state"><div class="emoji">👥</div>جارٍ جلب الأعضاء...</div>
                            </div>
                            <div class="col-footer">
                                <form method="POST" action="/update_status/{{ name }}">
                                    <select name="status_type" style="width:100%; margin-bottom:6px;">
                                        <option value="online">🟢 متصل</option>
                                        <option value="idle">🟡 خامل</option>
                                        <option value="dnd">🔴 عدم الإزعاج</option>
                                        <option value="invisible">⚫ مخفي</option>
                                    </select>
                                    <input type="text" name="status_text" placeholder="حالة النشاط..." style="width:100%; margin-bottom:6px;">
                                    <button type="submit" class="btn-primary" style="width:100%;">تحديث الحالة</button>
                                </form>
                            </div>
                        </div>

                    </div>
                </div>
            </div>

            <!-- تبويب الهوية -->
            <div class="tab-content" id="tab-{{ name }}-identity">
                <form method="POST" action="/update_identity/{{ name }}">
                    <div class="identity-grid">
                        <div class="identity-form-group">
                            <label>🏷️ اسم البوت (Username)</label>
                            <input type="text" name="new_username" placeholder="الاسم الجديد على ديسكورد">
                        </div>
                        <div class="identity-form-group">
                            <label>🖼️ رابط الصورة الشخصية (Avatar URL)</label>
                            <input type="text" name="new_avatar" placeholder="https://i.imgur.com/example.png">
                        </div>
                        <div class="identity-form-group">
                            <label>📝 البيو / وصف البوت</label>
                            <textarea name="new_bio" placeholder="اكتب وصفاً مختصراً للبوت..."></textarea>
                        </div>
                        <div class="identity-form-group">
                            <label>🎨 رابط خلفية البروفايل (Banner URL)</label>
                            <input type="text" name="new_banner" placeholder="https://i.imgur.com/banner.png">
                        </div>
                        <div style="grid-column: 1/-1;">
                            <button type="submit" class="btn-success" style="width:100%; padding: 13px;">✨ تحديث الهوية بالكامل</button>
                        </div>
                    </div>
                </form>
            </div>

            <!-- تبويب الإجراءات -->
            <div class="tab-content" id="tab-{{ name }}-actions">
                <div style="padding: 20px; display: grid; grid-template-columns: 1fr 1fr; gap: 16px;">

                    <!-- إرسال رسالة في قناة -->
                    <div style="background: var(--bg-panel); border-radius: 10px; padding: 15px; border: 1px solid var(--border);">
                        <div style="font-weight: 700; margin-bottom: 12px;">📢 إرسال رسالة في قناة</div>
                        <input type="text" id="ch-id-{{ name }}" placeholder="معرّف القناة (Channel ID)" style="width:100%; margin-bottom:8px;">
                        <textarea id="ch-msg-{{ name }}" placeholder="محتوى الرسالة..." style="width:100%; height:80px; resize:none; margin-bottom:8px;"></textarea>
                        <button class="btn-primary" style="width:100%;" onclick="sendToChannel('{{ name }}')">إرسال في القناة ✉️</button>
                    </div>

                    <!-- طرد عضو -->
                    <div style="background: var(--bg-panel); border-radius: 10px; padding: 15px; border: 1px solid var(--border);">
                        <div style="font-weight: 700; margin-bottom: 12px;">🚫 طرد عضو من السيرفر</div>
                        <input type="text" id="kick-guild-{{ name }}" placeholder="معرّف السيرفر (Guild ID)" style="width:100%; margin-bottom:8px;">
                        <input type="text" id="kick-user-{{ name }}" placeholder="معرّف المستخدم (User ID)" style="width:100%; margin-bottom:8px;">
                        <input type="text" id="kick-reason-{{ name }}" placeholder="سبب الطرد..." style="width:100%; margin-bottom:8px;">
                        <button class="btn-danger" style="width:100%;" onclick="kickUser('{{ name }}')">طرد العضو 🚫</button>
                    </div>

                    <!-- بان عضو -->
                    <div style="background: var(--bg-panel); border-radius: 10px; padding: 15px; border: 1px solid var(--border);">
                        <div style="font-weight: 700; margin-bottom: 12px;">⛔ حظر عضو من السيرفر</div>
                        <input type="text" id="ban-guild-{{ name }}" placeholder="معرّف السيرفر (Guild ID)" style="width:100%; margin-bottom:8px;">
                        <input type="text" id="ban-user-{{ name }}" placeholder="معرّف المستخدم (User ID)" style="width:100%; margin-bottom:8px;">
                        <input type="text" id="ban-reason-{{ name }}" placeholder="سبب الحظر..." style="width:100%; margin-bottom:8px;">
                        <button class="btn-danger" style="width:100%;" onclick="banUser('{{ name }}')">حظر العضو ⛔</button>
                    </div>

                    <!-- حذف رسائل -->
                    <div style="background: var(--bg-panel); border-radius: 10px; padding: 15px; border: 1px solid var(--border);">
                        <div style="font-weight: 700; margin-bottom: 12px;">🗑️ مسح رسائل من قناة</div>
                        <input type="text" id="purge-ch-{{ name }}" placeholder="معرّف القناة (Channel ID)" style="width:100%; margin-bottom:8px;">
                        <input type="number" id="purge-count-{{ name }}" placeholder="عدد الرسائل (1-100)" min="1" max="100" style="width:100%; margin-bottom:8px;">
                        <button class="btn-warn" style="width:100%;" onclick="purgeMessages('{{ name }}')">مسح الرسائل 🗑️</button>
                    </div>

                </div>
            </div>

        </div>
        {% endfor %}

    {% else %}
        <!-- شاشة الترحيب -->
        <div class="welcome-card">
            <div style="font-size: 70px; margin-bottom: 15px;">🤖</div>
            <h2>مرحباً في Discord Master</h2>
            <p>لا يوجد بوت مرتبط بعد — أضف توكن البوت أعلاه للبدء</p>
        </div>
    {% endif %}
</div>

<!-- ===== JavaScript ===== -->
<script>
// الساعة
function updateClock() {
    const now = new Date();
    document.getElementById('clock').textContent = now.toLocaleTimeString('ar-SA');
}
setInterval(updateClock, 1000);
updateClock();

// إشعار
function toast(msg, type='success') {
    const el = document.getElementById('toast');
    document.getElementById('toast-icon').textContent = type === 'success' ? '✅' : '❌';
    document.getElementById('toast-msg').textContent = msg;
    el.className = 'toast ' + type + ' show';
    setTimeout(() => el.classList.remove('show'), 3500);
}

// تبديل التبويبات
function switchTab(botName, tabName) {
    const card = document.getElementById('card-' + botName);
    card.querySelectorAll('.bot-tab').forEach((t, i) => {
        const tabs = ['monitor', 'identity', 'actions'];
        t.classList.toggle('active', tabs[i] === tabName);
    });
    card.querySelectorAll('.tab-content').forEach(tc => tc.classList.remove('active'));
    document.getElementById('tab-' + botName + '-' + tabName).classList.add('active');
}

// تحديث واجهة البوت
function updateUI(botName) {
    fetch('/get_data/' + botName)
        .then(r => r.json())
        .then(data => {
            // ===== القنوات =====
            const chanBox = document.getElementById('channels-' + botName);
            document.getElementById('chan-count-' + botName).textContent = data.channels.length;
            if(data.channels.length === 0) {
                chanBox.innerHTML = '<div class="empty-state"><div class="emoji">📁</div>لا توجد قنوات</div>';
            } else {
                chanBox.innerHTML = data.channels.map(c => `
                    <div class="channel-item">
                        <div class="ch-name">
                            <span class="prefix">${c.type === 'text' ? '#' : '🔊'}</span>
                            ${c.name}
                        </div>
                        <button class="btn-danger" style="padding:3px 8px; font-size:0.72rem;"
                            onclick="deleteChannel('${botName}', '${c.id}')">حذف</button>
                    </div>`).join('');
            }

            // ===== الرسائل =====
            const msgBox = document.getElementById('messages-' + botName);
            document.getElementById('msg-count-' + botName).textContent = data.messages.length;
            if(data.messages.length === 0) {
                msgBox.innerHTML = '<div class="empty-state"><div class="emoji">💬</div>لا توجد رسائل بعد</div>';
            } else {
                msgBox.innerHTML = data.messages.slice(-30).reverse().map(m => {
                    let imgs = (m.attachments || []).map(url =>
                        `<img src="${url}" class="msg-img" onclick="window.open('${url}')">`
                    ).join('');
                    return `
                        <div class="message ${m.is_deleted ? 'msg-deleted' : ''} ${m.is_bot ? 'msg-bot' : ''}">
                            <img src="${m.avatar || 'https://cdn.discordapp.com/embed/avatars/0.png'}" class="msg-avatar">
                            <div class="msg-content-wrap">
                                <div class="msg-meta">
                                    <span class="msg-author">${m.user}</span>
                                    ${m.is_bot ? '<span class="bot-tag">BOT</span>' : ''}
                                    ${m.is_deleted ? '<span class="del-tag">🗑️ محذوفة</span>' : ''}
                                    <span class="msg-time">${m.time}</span>
                                </div>
                                <div class="msg-text">${m.content || '<i style="color:var(--muted)">لا يوجد نص</i>'}</div>
                                ${imgs}
                            </div>
                        </div>`;
                }).join('');
            }

            // ===== الأعضاء =====
            const memBox = document.getElementById('members-' + botName);
            document.getElementById('mem-count-' + botName).textContent = data.members.length;
            if(data.members.length === 0) {
                memBox.innerHTML = '<div class="empty-state"><div class="emoji">👥</div>لا يوجد أعضاء</div>';
            } else {
                memBox.innerHTML = data.members.slice(0, 80).map(m => `
                    <div class="member-item">
                        <div class="status-dot ${m.status}"></div>
                        <div class="member-name">${m.name}</div>
                        <div class="member-guild" title="${m.guild}">${m.guild ? m.guild.substring(0,12) + (m.guild.length > 12 ? '...' : '') : ''}</div>
                        <div class="member-actions">
                            <button class="btn-warn" onclick="quickKick('${botName}','${m.guild_id}','${m.id}')">طرد</button>
                            <button class="btn-danger" onclick="quickBan('${botName}','${m.guild_id}','${m.id}')">بان</button>
                        </div>
                    </div>`).join('');
            }
        });
}

// تحديث تلقائي كل 3 ثوانٍ
{% for name in bots.keys() %}
setInterval(() => updateUI('{{ name }}'), 3000);
updateUI('{{ name }}');
{% endfor %}

// ===== وظائف الإجراءات =====

function sendDM(botName) {
    const id = document.getElementById('dm-id-' + botName).value.trim();
    const msg = document.getElementById('dm-msg-' + botName).value.trim();
    if(!id || !msg) { toast('الرجاء إدخال الآيدي والرسالة', 'error'); return; }
    fetch('/send_direct/' + botName, {
        method: 'POST',
        headers: {'Content-Type': 'application/x-www-form-urlencoded'},
        body: `user_id=${encodeURIComponent(id)}&message=${encodeURIComponent(msg)}`
    }).then(r => r.text()).then(res => {
        toast(res.includes('خطأ') ? res : 'تم إرسال الرسالة الخاصة ✉️', res.includes('خطأ') ? 'error' : 'success');
        document.getElementById('dm-msg-' + botName).value = '';
    });
}

function sendToChannel(botName) {
    const chId = document.getElementById('ch-id-' + botName).value.trim();
    const msg = document.getElementById('ch-msg-' + botName).value.trim();
    if(!chId || !msg) { toast('الرجاء إدخال معرّف القناة والرسالة', 'error'); return; }
    fetch('/send_channel/' + botName, {
        method: 'POST',
        headers: {'Content-Type': 'application/x-www-form-urlencoded'},
        body: `channel_id=${encodeURIComponent(chId)}&message=${encodeURIComponent(msg)}`
    }).then(r => r.text()).then(res => {
        toast(res.includes('خطأ') ? res : '📢 تم إرسال الرسالة في القناة!', res.includes('خطأ') ? 'error' : 'success');
        document.getElementById('ch-msg-' + botName).value = '';
    });
}

function deleteChannel(botName, chId) {
    if(!confirm('هل أنت متأكد من حذف هذه القناة؟')) return;
    fetch('/delete_channel/' + botName + '/' + chId, {method: 'POST'})
        .then(() => { toast('✅ تم حذف القناة بنجاح'); updateUI(botName); });
}

function createChannel(botName, type) {
    const name = document.getElementById('new-ch-' + botName).value.trim();
    if(!name) { toast('الرجاء إدخال اسم القناة', 'error'); return; }
    fetch('/create_channel/' + botName + '/' + type + '/' + encodeURIComponent(name), {method: 'POST'})
        .then(() => { toast('✅ تم إنشاء القناة: ' + name); updateUI(botName); document.getElementById('new-ch-' + botName).value = ''; });
}

function kickUser(botName) {
    const gId = document.getElementById('kick-guild-' + botName).value.trim();
    const uId = document.getElementById('kick-user-' + botName).value.trim();
    const reason = document.getElementById('kick-reason-' + botName).value.trim();
    if(!gId || !uId) { toast('الرجاء إدخال معرّفات السيرفر والمستخدم', 'error'); return; }
    fetch('/kick/' + botName + '/' + gId + '/' + uId, {
        method: 'POST',
        headers: {'Content-Type': 'application/x-www-form-urlencoded'},
        body: `reason=${encodeURIComponent(reason || 'بدون سبب')}`
    }).then(() => toast('🚫 تم طرد المستخدم'));
}

function quickKick(botName, guildId, userId) {
    if(!confirm('هل تريد طرد هذا العضو؟')) return;
    fetch('/kick/' + botName + '/' + guildId + '/' + userId, {
        method: 'POST',
        headers: {'Content-Type': 'application/x-www-form-urlencoded'},
        body: 'reason=Kicked from Dashboard'
    }).then(() => { toast('🚫 تم الطرد بنجاح'); updateUI(botName); });
}

function banUser(botName) {
    const gId = document.getElementById('ban-guild-' + botName).value.trim();
    const uId = document.getElementById('ban-user-' + botName).value.trim();
    const reason = document.getElementById('ban-reason-' + botName).value.trim();
    if(!gId || !uId) { toast('الرجاء إدخال معرّفات السيرفر والمستخدم', 'error'); return; }
    fetch('/ban/' + botName + '/' + gId + '/' + uId, {
        method: 'POST',
        headers: {'Content-Type': 'application/x-www-form-urlencoded'},
        body: `reason=${encodeURIComponent(reason || 'بدون سبب')}`
    }).then(() => toast('⛔ تم حظر المستخدم'));
}

function quickBan(botName, guildId, userId) {
    if(!confirm('هل تريد حظر هذا العضو نهائياً؟')) return;
    fetch('/ban/' + botName + '/' + guildId + '/' + userId, {
        method: 'POST',
        headers: {'Content-Type': 'application/x-www-form-urlencoded'},
        body: 'reason=Banned from Dashboard'
    }).then(() => { toast('⛔ تم الحظر بنجاح'); updateUI(botName); });
}

function purgeMessages(botName) {
    const chId = document.getElementById('purge-ch-' + botName).value.trim();
    const count = document.getElementById('purge-count-' + botName).value.trim();
    if(!chId || !count) { toast('الرجاء إدخال معرّف القناة والعدد', 'error'); return; }
    if(!confirm(`هل تريد حذف ${count} رسالة من هذه القناة؟`)) return;
    fetch('/purge/' + botName, {
        method: 'POST',
        headers: {'Content-Type': 'application/x-www-form-urlencoded'},
        body: `channel_id=${encodeURIComponent(chId)}&count=${count}`
    }).then(r => r.text()).then(res => toast(res));
}
</script>
</body>
</html>
"""

# ===================================================
#  منطق البوت
# ===================================================

def create_bot(name):
    intents = discord.Intents.all()
    bot = commands.Bot(command_prefix="!", intents=intents)

    @bot.event
    async def on_ready():
        print(f"[✅] البوت '{name}' متصل كـ {bot.user}")

    @bot.event
    async def on_message(message):
        attachment_urls = [a.url for a in message.attachments]
        msg_data = {
            "id": message.id,
            "user": message.author.display_name,
            "avatar": str(message.author.display_avatar.url),
            "content": message.content,
            "time": datetime.now().strftime("%H:%M"),
            "is_bot": message.author.bot,
            "is_deleted": False,
            "attachments": attachment_urls
        }
        if name in bots:
            bots[name]["messages"].append(msg_data)
            if len(bots[name]["messages"]) > 100:
                bots[name]["messages"].pop(0)
        await bot.process_commands(message)

    @bot.event
    async def on_message_delete(message):
        if name in bots:
            for m in bots[name]["messages"]:
                if m["id"] == message.id:
                    m["is_deleted"] = True
                    break

    return bot


# ===================================================
#  Flask Routes
# ===================================================

@app.route("/")
def index():
    return render_template_string(HTML, bots=bots)


@app.route("/add_bot", methods=["POST"])
def add_bot():
    name = request.form.get("bot_name", "").strip()
    token = request.form.get("bot_token", "").strip()
    if name and token and name not in bots:
        bot_instance = create_bot(name)
        loop = asyncio.new_event_loop()
        def run_bot(b, t, l):
            asyncio.set_event_loop(l)
            try:
                l.run_until_complete(b.start(t))
            except Exception as e:
                print(f"[Error] {name}: {e}")
        threading.Thread(target=run_bot, args=(bot_instance, token, loop), daemon=True).start()
        bots[name] = {"bot": bot_instance, "loop": loop, "messages": []}
    return redirect("/")


@app.route("/remove_bot/<name>", methods=["POST"])
def remove_bot(name):
    if name in bots:
        try:
            asyncio.run_coroutine_threadsafe(bots[name]["bot"].close(), bots[name]["loop"])
        except: pass
        del bots[name]
    return redirect("/")


@app.route("/get_data/<bot_name>")
def get_data(bot_name):
    if bot_name not in bots:
        return jsonify({"channels": [], "members": [], "messages": []})
    bot = bots[bot_name]["bot"]

    channels = []
    members = []

    for guild in bot.guilds:
        # القنوات
        for c in guild.channels:
            if isinstance(c, discord.TextChannel):
                channels.append({"name": c.name, "id": str(c.id), "type": "text"})
            elif isinstance(c, discord.VoiceChannel):
                channels.append({"name": c.name, "id": str(c.id), "type": "voice"})

        # الأعضاء
        for m in guild.members:
            members.append({
                "name": m.display_name,
                "id": str(m.id),
                "guild": guild.name,
                "guild_id": str(guild.id),
                "status": str(m.status)
            })

    return jsonify({
        "channels": channels,
        "members": members[:150],
        "messages": bots[bot_name]["messages"]
    })


@app.route("/send_direct/<bot_name>", methods=["POST"])
def send_direct(bot_name):
    user_id = request.form.get("user_id", "")
    msg = request.form.get("message", "")
    if bot_name not in bots:
        return "البوت غير موجود"
    async def action():
        try:
            user = await bots[bot_name]["bot"].fetch_user(int(user_id))
            await user.send(msg)
            return "تم الإرسال بنجاح ✅"
        except Exception as e:
            return f"خطأ: {e}"
    future = asyncio.run_coroutine_threadsafe(action(), bots[bot_name]["loop"])
    try:
        return future.result(timeout=10)
    except:
        return "خطأ في الإرسال"


@app.route("/send_channel/<bot_name>", methods=["POST"])
def send_channel(bot_name):
    channel_id = request.form.get("channel_id", "")
    msg = request.form.get("message", "")
    if bot_name not in bots:
        return "البوت غير موجود"
    async def action():
        try:
            channel = bots[bot_name]["bot"].get_channel(int(channel_id))
            if not channel:
                channel = await bots[bot_name]["bot"].fetch_channel(int(channel_id))
            await channel.send(msg)
            return "تم الإرسال في القناة ✅"
        except Exception as e:
            return f"خطأ: {e}"
    future = asyncio.run_coroutine_threadsafe(action(), bots[bot_name]["loop"])
    try:
        return future.result(timeout=10)
    except:
        return "خطأ في الإرسال"


@app.route("/update_status/<name>", methods=["POST"])
def update_status(name):
    st_type = request.form.get("status_type", "online")
    st_text = request.form.get("status_text", "")
    if name in bots:
        status_map = {
            "online": discord.Status.online,
            "idle": discord.Status.idle,
            "dnd": discord.Status.dnd,
            "invisible": discord.Status.invisible
        }
        asyncio.run_coroutine_threadsafe(
            bots[name]["bot"].change_presence(
                status=status_map.get(st_type, discord.Status.online),
                activity=discord.Game(name=st_text) if st_text else None
            ),
            bots[name]["loop"]
        )
    return redirect("/")


@app.route("/update_identity/<name>", methods=["POST"])
def update_identity(name):
    if name not in bots:
        return redirect("/")
    u_name  = request.form.get("new_username", "").strip()
    u_bio   = request.form.get("new_bio", "").strip()
    u_avatar= request.form.get("new_avatar", "").strip()

    bot = bots[name]["bot"]

    async def process():
        try:
            payload = {}
            if u_name:
                payload['username'] = u_name
            if u_avatar:
                async with aiohttp.ClientSession() as session:
                    async with session.get(u_avatar) as resp:
                        if resp.status == 200:
                            payload['avatar'] = await resp.read()
            if payload:
                await bot.user.edit(**payload)
            print(f"[✅] تم تحديث هوية البوت: {name}")
        except Exception as e:
            print(f"[Error] Identity: {e}")

    asyncio.run_coroutine_threadsafe(process(), bots[name]["loop"])
    return redirect("/")


@app.route("/delete_channel/<bot_name>/<ch_id>", methods=["POST"])
def delete_channel(bot_name, ch_id):
    if bot_name not in bots:
        return "بوت غير موجود"
    async def action():
        try:
            channel = bots[bot_name]["bot"].get_channel(int(ch_id))
            if channel:
                await channel.delete()
        except Exception as e:
            print(f"[Error] delete_channel: {e}")
    asyncio.run_coroutine_threadsafe(action(), bots[bot_name]["loop"])
    return "OK"


@app.route("/create_channel/<bot_name>/<ch_type>/<ch_name>", methods=["POST"])
def create_channel(bot_name, ch_type, ch_name):
    if bot_name not in bots:
        return "بوت غير موجود"
    async def action():
        try:
            guild = bots[bot_name]["bot"].guilds[0]
            if ch_type == 'text':
                await guild.create_text_channel(ch_name)
            else:
                await guild.create_voice_channel(ch_name)
        except Exception as e:
            print(f"[Error] create_channel: {e}")
    asyncio.run_coroutine_threadsafe(action(), bots[bot_name]["loop"])
    return "OK"


@app.route("/kick/<bot_name>/<guild_id>/<user_id>", methods=["POST"])
def kick_user(bot_name, guild_id, user_id):
    reason = request.form.get("reason", "No reason")
    if bot_name not in bots:
        return "بوت غير موجود"
    async def action():
        try:
            guild = bots[bot_name]["bot"].get_guild(int(guild_id))
            if not guild:
                return
            member = guild.get_member(int(user_id))
            if member:
                try:
                    await member.send(f"🚫 تم طردك من **{guild.name}**\n📋 السبب: {reason}")
                except: pass
                await member.kick(reason=reason)
        except Exception as e:
            print(f"[Error] kick: {e}")
    asyncio.run_coroutine_threadsafe(action(), bots[bot_name]["loop"])
    return "OK"


@app.route("/ban/<bot_name>/<guild_id>/<user_id>", methods=["POST"])
def ban_user(bot_name, guild_id, user_id):
    reason = request.form.get("reason", "No reason")
    if bot_name not in bots:
        return "بوت غير موجود"
    async def action():
        try:
            guild = bots[bot_name]["bot"].get_guild(int(guild_id))
            if not guild:
                return
            member = guild.get_member(int(user_id))
            if member:
                try:
                    await member.send(f"⛔ تم حظرك من **{guild.name}**\n📋 السبب: {reason}")
                except: pass
                await member.ban(reason=reason)
        except Exception as e:
            print(f"[Error] ban: {e}")
    asyncio.run_coroutine_threadsafe(action(), bots[bot_name]["loop"])
    return "OK"


@app.route("/purge/<bot_name>", methods=["POST"])
def purge_messages(bot_name):
    channel_id = request.form.get("channel_id", "")
    count = int(request.form.get("count", 10))
    if bot_name not in bots:
        return "بوت غير موجود"
    async def action():
        try:
            channel = bots[bot_name]["bot"].get_channel(int(channel_id))
            if not channel:
                channel = await bots[bot_name]["bot"].fetch_channel(int(channel_id))
            deleted = await channel.purge(limit=min(count, 100))
            return f"✅ تم حذف {len(deleted)} رسالة"
        except Exception as e:
            return f"خطأ: {e}"
    future = asyncio.run_coroutine_threadsafe(action(), bots[bot_name]["loop"])
    try:
        return future.result(timeout=15)
    except:
        return "خطأ في المسح"


# ===================================================
#  التشغيل
# ===================================================
if __name__ == "__main__":
    print("=" * 50)
    print("  🚀 Discord Master Dashboard")
    print("  🌐 http://localhost:5000")
    print("=" * 50)
    app.run(debug=False, host="0.0.0.0", port=5000)
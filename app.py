from flask import Flask, render_template, request, jsonify, redirect, url_for
from zapv2 import ZAPv2

import requests

app = Flask(__name__)

# إعداد ZAP
zap = ZAPv2(apikey='1vjv1fle4uepc49r4sf6f23oin', proxies={'http': 'http://127.0.0.1:8080', 'https': 'http://127.0.0.1:8080'})

# الصفحة الرئيسية
@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

# بدء الفحص
@app.route('/scan', methods=['POST'])
def scan():
    target_url = request.form['target_url']

    # التحقق مما إذا كان الموقع موجود
    try:
        response = requests.get(target_url)
        if response.status_code != 200:
            return jsonify({'error': f"الموقع غير متاح. رمز الحالة: {response.status_code}"}), 400
    except requests.exceptions.RequestException as e:
        return jsonify({'error': f"خطأ أثناء محاولة الوصول إلى الموقع: {e}"}), 400

    # فتح الرابط
    zap.urlopen(target_url)
    print(f"تم فتح الرابط: {target_url}")

    # بدء الفحص النشط
    scan_id = zap.ascan.scan(target_url)
    print(f"معرّف الفحص: {scan_id}")

    # إعادة معرّف الفحص للمستخدم
    return jsonify({'scan_id': scan_id})

# متابعة حالة الفحص
@app.route('/scan_status', methods=['GET'])
def scan_status():
    scan_id = request.args.get('scan_id')
    status = zap.ascan.status(scan_id)
    return jsonify({'status': status})

# عرض النتائج
@app.route('/results', methods=['GET'])
def results():
    scan_id = request.args.get('scan_id')
    target_url = request.args.get('target_url')

    # الحصول على نتائج الفحص النشط
    alerts = zap.core.alerts(baseurl=target_url)

    # تجهيز بيانات التنبيهات
    alerts_info = []
    for alert in alerts:
        alert_info = {
            'name': alert['alert'],
            'risk': alert['risk'],
            'description': alert['description'],
            'solution': alert['solution']
        }
        alerts_info.append(alert_info)

    return render_template('result.html', alerts=alerts_info)

if __name__ == '__main__':
    app.run(debug=True)

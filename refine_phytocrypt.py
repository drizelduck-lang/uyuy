<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>PhytoCrypt – Signature Result</title>

    <!-- Use your existing theme -->
    <link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}">
</head>

<body>
<div class="container">

    <!-- HEADER -->
    <header class="header">
        <img src="{{ url_for('static', filename='PHYTOCRYPT LOGO (PLAIN) (1).png') }}" alt="Logo" class="logo">
        <h1>Signature Verification Result</h1>
    </header>

    <!-- STATUS BOX -->
    {% if result %}
        {% set box_class = 
            "alert-success" if result.decision in ["ACCEPTED","REGISTERED"] else 
            "alert-warning" if result.decision == "UNCERTAIN" else 
            "alert-danger"
        %}
        <div class="alert {{ box_class }}" style="margin-top:1.5em;">
            <strong>Status:</strong> {{ result.decision }} <br>
            {% if result.reason %}
                <strong>Details:</strong> {{ result.reason }}
            {% endif %}
        </div>
    {% endif %}

    <!-- SIGNATURE INFO -->
    <div class="card" style="margin-top:1.5em;">
        <h2>Signature Information</h2>

        <p><strong>Signer ID:</strong> {{ signer_id }}</p>
        <p><strong>Hashing Mode:</strong> {{ hash_mode }}</p>

        {% if result.confidence %}
            <p><strong>Confidence Score:</strong> {{ result.confidence }}%</p>
        {% endif %}
        {% if result.distance %}
            <p><strong>Feature Distance:</strong> {{ result.distance }}</p>
        {% endif %}
    </div>

    <!-- IMAGE PREVIEWS -->
    <div class="grid-container" style="margin-top:1.5em;">
        <div class="card">
            <h3>Stored Reference Signature</h3>
            {% if result.stored_image %}
                <img src="{{ url_for('serve_upload', filename=result.stored_image) }}"
                     alt="Stored Signature"
                     class="preview-image">
            {% else %}
                <p>No stored reference image.</p>
            {% endif %}
        </div>

        <div class="card">
            <h3>Uploaded Signature</h3>
            {% if result.uploaded_image %}
                <img src="{{ url_for('serve_upload', filename=result.uploaded_image) }}"
                     alt="Uploaded Signature"
                     class="preview-image">
            {% else %}
                <p>No uploaded image.</p>
            {% endif %}
        </div>
    </div>

    <!-- FEATURES -->
    {% if result.features %}
        <div class="card" style="margin-top:1.5em;">
            <h2>Extracted Signature Features</h2>
            <pre class="hash-output">{{ result.features | tojson(indent=2) }}</pre>
        </div>
    {% endif %}

    <!-- HASHES -->
    {% if result.hashes %}
        <div class="card" style="margin-top:1.5em;">
            <h2>Hash Outputs</h2>

            {% if result.hashes.bio_key %}
                <p><strong>Bio-Key:</strong></p>
                <pre class="hash-output">{{ result.hashes.bio_key }}</pre>
            {% endif %}

            {% if result.hashes.hybrid_hash %}
                <p><strong>Hybrid Hash:</strong></p>
                <pre class="hash-output">{{ result.hashes.hybrid_hash }}</pre>
            {% endif %}

            {% if result.hashes.hmac %}
                <p><strong>File HMAC:</strong></p>
                <pre class="hash-output">{{ result.hashes.hmac }}</pre>
            {% endif %}
        </div>
    {% endif %}

    <!-- MATCHED SAMPLES -->
    {% if result.matches %}
        <div class="card" style="margin-top:1.5em;">
            <h2>Matched Samples</h2>

            {% for match in result.matches %}
                <div style="margin-bottom:1em;">
                    <strong>File:</strong> {{ match.sample_file_name }}<br>
                    <strong>Distance:</strong> {{ match.phash_distance }}<br>
                </div>
            {% endfor %}
        </div>
    {% endif %}

    <!-- BACK BUTTON -->
    <div style="text-align:center; margin-top:2em;">
        <a href="/" class="btn btn-secondary">Back to Home</a>
    </div>

</div>
</body>
</html>

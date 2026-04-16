document.addEventListener('DOMContentLoaded', () => {

    // --- Dashboard logic ---
    const dropZone = document.getElementById('drop-zone');
    const fileUpload = document.getElementById('file-upload');
    const fileInfo = document.getElementById('file-info');
    const scanBtn = document.getElementById('scan-btn');
    const resultSection = document.getElementById('result-section');
    
    let selectedFile = null;

    if (dropZone && fileUpload) {
        dropZone.addEventListener('dragover', (e) => {
            e.preventDefault();
            dropZone.classList.add('dragover');
        });
        ['dragleave', 'dragend'].forEach(type => {
            dropZone.addEventListener(type, () => dropZone.classList.remove('dragover'));
        });
        dropZone.addEventListener('drop', (e) => {
            e.preventDefault();
            dropZone.classList.remove('dragover');
            if(e.dataTransfer.files.length) {
                fileUpload.files = e.dataTransfer.files;
                handleFileSelect();
            }
        });
        fileUpload.addEventListener('change', handleFileSelect);

        function handleFileSelect() {
            if(fileUpload.files.length > 0) {
                selectedFile = fileUpload.files[0];
                fileInfo.textContent = `Selected: ${selectedFile.name}`;
                scanBtn.disabled = false;
            }
        }

        scanBtn.addEventListener('click', async () => {
            if(!selectedFile) return;
            
            const formData = new FormData();
            formData.append('document', selectedFile);
            
            scanBtn.style.display = 'none';
            document.getElementById('loader').style.display = 'block';
            document.getElementById('scan-error').textContent = '';
            
            try {
                const res = await fetch('/api/detect-ai', {
                    method: 'POST',
                    body: formData
                });
                const data = await res.json();
                
                if(data.success) {
                    displayScanResult(data);
                    fetchHistory();
                } else {
                    document.getElementById('scan-error').textContent = data.error || 'Check failed.';
                }
            } catch (err) {
                document.getElementById('scan-error').textContent = 'Network or server error.';
            } finally {
                scanBtn.style.display = 'block';
                document.getElementById('loader').style.display = 'none';
            }
        });
    }

    function displayScanResult(data) {
        resultSection.style.display = 'block';
        document.getElementById('ai-value').textContent = data.ai_percentage;
        document.getElementById('total-words').textContent = data.total_words;
        document.getElementById('res-filename').textContent = data.filename;
        
        const circle = document.getElementById('progress-circle');
        const radius = circle.r.baseVal.value;
        const circumference = radius * 2 * Math.PI;
        const offset = circumference - (data.ai_percentage / 100) * circumference;
        
        // Update color based on score (Green < 30, Yellow < 70, Red >= 70)
        let color = 'var(--success)';
        if(data.ai_percentage >= 70) color = 'var(--danger)';
        else if(data.ai_percentage >= 30) color = '#d29922';
        
        circle.style.stroke = color;
        
        // Timeout to allow browser to render block display before animating
        setTimeout(() => {
            circle.style.strokeDashoffset = offset;
        }, 50);
    }

    // --- History Table Logic ---
    const historyTable = document.getElementById('history-table');
    if (historyTable) {
        fetchHistory();
    }

    async function fetchHistory() {
        try {
            const res = await fetch('/api/history');
            const data = await res.json();
            if(data.success && data.scans.length) {
                const tbody = historyTable.querySelector('tbody');
                tbody.innerHTML = '';
                data.scans.forEach(scan => {
                    let colorCode = scan.ai_percentage >= 70 ? 'var(--danger)' : (scan.ai_percentage >= 30 ? '#d29922' : 'var(--success)');
                    const tr = document.createElement('tr');
                    tr.innerHTML = `
                        <td>${scan.filename}</td>
                        <td style="color:${colorCode}; font-weight:bold;">${scan.ai_percentage}%</td>
                        <td>${new Date(scan.timestamp).toLocaleString()}</td>
                    `;
                    tbody.appendChild(tr);
                });
            }
        } catch (e) {}
    }


    // --- Steganography Tabs Logic ---
    const tabs = document.querySelectorAll('.tab-btn');
    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
            document.querySelectorAll('.panel').forEach(p => p.classList.remove('active'));
            
            tab.classList.add('active');
            document.getElementById(tab.dataset.target).classList.add('active');
        });
    });

    // --- Encode Logic ---
    const encodeBtn = document.getElementById('encode-btn');
    if(encodeBtn) {
        encodeBtn.addEventListener('click', async () => {
            const fileInput = document.getElementById('encode-img');
            const secretMsg = document.getElementById('secret-msg').value;
            const errorP = document.getElementById('encode-error');
            
            if(!fileInput.files.length || !secretMsg.trim()) {
                errorP.textContent = "Please select an image and enter a message.";
                return;
            }
            
            errorP.textContent = "";
            encodeBtn.disabled = true;
            document.getElementById('encode-loader').style.display = 'block';
            
            const formData = new FormData();
            formData.append('image', fileInput.files[0]);
            formData.append('secret_text', secretMsg);
            
            try {
                const res = await fetch('/api/stegano/encode', {
                    method: 'POST',
                    body: formData
                });
                
                if(res.ok) {
                    const blob = await res.blob();
                    const url = window.URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.style.display = 'none';
                    a.href = url;
                    a.download = `encoded_${fileInput.files[0].name}`;
                    document.body.appendChild(a);
                    a.click();
                    window.URL.revokeObjectURL(url);
                    // clear forms
                    fileInput.value = '';
                    document.getElementById('secret-msg').value = '';
                } else {
                    const data = await res.json();
                    errorP.textContent = data.error || 'Encoding failed.';
                }
            } catch(e) {
                errorP.textContent = "Network error.";
            } finally {
                encodeBtn.disabled = false;
                document.getElementById('encode-loader').style.display = 'none';
            }
        });
    }

    // --- Decode Logic ---
    const decodeBtn = document.getElementById('decode-btn');
    if(decodeBtn) {
        decodeBtn.addEventListener('click', async () => {
            const fileInput = document.getElementById('decode-img');
            const errorP = document.getElementById('decode-error');
            const resultBox = document.getElementById('decode-result');
            
            if(!fileInput.files.length) {
                errorP.textContent = "Please select an encoded image.";
                return;
            }
            errorP.textContent = "";
            resultBox.style.display = "none";
            
            decodeBtn.disabled = true;
            document.getElementById('decode-loader').style.display = 'block';
            
            const formData = new FormData();
            formData.append('image', fileInput.files[0]);
            
            try {
                const res = await fetch('/api/stegano/advanced-analyze', {
                    method: 'POST',
                    body: formData
                });
                const data = await res.json();
                if(data.success && data.analysis) {
                    resultBox.style.display = "block";
                    document.getElementById('revealed-msg').textContent = JSON.stringify(data.analysis, null, 2);
                } else {
                    errorP.textContent = data.error || 'Advanced Scan failed.';
                }
            } catch(e) {
                errorP.textContent = "Network error.";
            } finally {
                decodeBtn.disabled = false;
                document.getElementById('decode-loader').style.display = 'none';
            }
        });
        
        const copyStegBtn = document.getElementById('copy-steg-json-btn');
        if (copyStegBtn) {
            copyStegBtn.addEventListener('click', () => {
                const text = document.getElementById('revealed-msg').textContent;
                navigator.clipboard.writeText(text).then(() => {
                    copyStegBtn.innerHTML = '<i class="fa-solid fa-check"></i> Copied!';
                    setTimeout(() => { copyStegBtn.innerHTML = '<i class="fa-solid fa-copy"></i> Copy JSON'; }, 2000);
                });
            });
        }
    }
});

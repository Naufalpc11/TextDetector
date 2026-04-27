<template>
  <div class="digit-classifier">
    <div class="container">
      <!-- Header -->
      <div class="header">
        <div class="header-content">
          <h1 class="title">✨ MNIST Digit Classifier</h1>
          <p class="subtitle">Klasifikasi digit tulisan tangan dengan model YOLO terdepan</p>
        </div>
      </div>

      <!-- Main Content -->
      <div class="main-grid">
        <!-- Upload Section -->
        <div class="upload-section">
          <div class="card">
            <div class="card-header">
              <h2>📤 Upload Gambar</h2>
              <p class="card-subtitle">Pilih gambar digit 0-9 dari perangkat Anda</p>
            </div>

            <div class="upload-area" 
              @dragover.prevent="isDragging = true"
              @dragleave.prevent="isDragging = false"
              @drop.prevent="handleDrop"
              :class="{ 'is-dragging': isDragging }">
              <div class="upload-icon">📁</div>
              <p class="upload-text">Drag & drop gambar di sini</p>
              <p class="upload-or">atau</p>
              <label class="upload-button">
                Pilih Gambar
                <input type="file" @change="handleFileSelect" accept="image/*" />
              </label>
            </div>

            <!-- File Info -->
            <div v-if="selectedFile" class="file-info">
              <div class="info-item">
                <span class="info-label">File:</span>
                <span class="info-value">{{ selectedFile.name }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">Ukuran:</span>
                <span class="info-value">{{ formatFileSize(selectedFile.size) }}</span>
              </div>
            </div>

            <!-- Classify Button -->
            <button 
              class="classify-button" 
              @click="classifyImage" 
              :disabled="!selectedFile || loading"
              :class="{ 'is-loading': loading }">
              <span v-if="!loading" class="button-icon">🚀</span>
              <span v-else class="spinner"></span>
              {{ loading ? 'Menganalisis...' : 'Analisis Digit' }}
            </button>
          </div>
        </div>

        <!-- Preview Section -->
        <div v-if="selectedFile" class="preview-section">
          <div class="card">
            <div class="card-header">
              <h2>👁️ Preview</h2>
            </div>
            <div class="preview-wrapper">
              <img :src="imagePreview" alt="Preview" class="preview-image" />
            </div>
          </div>
        </div>

        <!-- Results Section -->
        <div v-if="result" class="result-section">
          <div class="card success-card">
            <div class="card-header success-header">
              <h2>✅ Hasil Klasifikasi</h2>
            </div>
            <div class="result-content">
              <div class="result-digit">
                <div class="digit-display">{{ result.angka }}</div>
                <p class="digit-label">Prediksi Digit</p>
              </div>
              <div class="result-confidence">
                <div class="confidence-bar">
                  <div class="confidence-fill" :style="{ width: extractConfidence(result.persentase_keyakinan) + '%' }"></div>
                </div>
                <p class="confidence-text">{{ result.persentase_keyakinan }}</p>
              </div>
              <div class="preprocessing-info">
                <p><strong>Auto-invert:</strong> {{ result.preprocessing?.auto_invert ? 'Ya' : 'Tidak' }}</p>
              </div>
            </div>
          </div>
        </div>

        <!-- Error Section -->
        <div v-if="error" class="error-section">
          <div class="card error-card">
            <div class="card-header error-header">
              <h2>⚠️ Terjadi Kesalahan</h2>
            </div>
            <div class="error-content">
              <p>{{ error }}</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Footer Info -->
      <div class="footer-info">
        <p>💡 <strong>Tips:</strong> Gunakan gambar digit tulisan tangan yang jelas untuk hasil terbaik</p>
        <p>🔗 Backend: <code>http://localhost:8000</code></p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import axios from 'axios'

const selectedFile = ref<File | null>(null)
const imagePreview = ref<string>('')
const result = ref<any>(null)
const error = ref<string>('')
const loading = ref<boolean>(false)
const isDragging = ref<boolean>(false)

const handleFileSelect = (event: Event) => {
  const target = event.target as HTMLInputElement
  if (target.files && target.files[0]) {
    processFile(target.files[0])
  }
}

const handleDrop = (event: DragEvent) => {
  isDragging.value = false
  if (event.dataTransfer?.files && event.dataTransfer.files[0]) {
    processFile(event.dataTransfer.files[0])
  }
}

const processFile = (file: File) => {
  if (!file.type.startsWith('image/')) {
    error.value = 'Silakan pilih file gambar yang valid'
    return
  }
  
  selectedFile.value = file
  const reader = new FileReader()
  reader.onload = (e) => {
    imagePreview.value = e.target?.result as string
  }
  reader.readAsDataURL(file)
  result.value = null
  error.value = ''
}

const classifyImage = async () => {
  if (!selectedFile.value) return

  loading.value = true
  error.value = ''
  result.value = null

  try {
    const formData = new FormData()
    formData.append('file', selectedFile.value)

    const response = await axios.post('http://localhost:8000/tebak-angka', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })

    if (response.data.status === 'sukses') {
      result.value = response.data
    } else {
      error.value = response.data.pesan || 'Terjadi kesalahan saat mengklasifikasi'
    }
  } catch (err: any) {
    error.value = err.response?.data?.pesan || err.message || 'Tidak dapat terhubung ke server'
  } finally {
    loading.value = false
  }
}

const formatFileSize = (bytes: number): string => {
  if (bytes === 0) return '0 Bytes'
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i]
}

const extractConfidence = (confString: string): number => {
  const num = parseFloat(confString)
  return isNaN(num) ? 0 : num
}
</script>

<style scoped>
* {
  box-sizing: border-box;
}

.digit-classifier {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 2rem 1rem;
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
}

/* Header */
.header {
  text-align: center;
  color: white;
  margin-bottom: 3rem;
}

.header-content {
  animation: slideInDown 0.6s ease-out;
}

.title {
  font-size: clamp(2rem, 5vw, 3.5rem);
  font-weight: 800;
  margin: 0 0 0.5rem;
  letter-spacing: -0.02em;
}

.subtitle {
  font-size: 1.1rem;
  opacity: 0.95;
  margin: 0;
  font-weight: 300;
}

/* Main Grid */
.main-grid {
  display: grid;
  gap: 2rem;
  grid-template-columns: 1fr;
}

@media (min-width: 900px) {
  .main-grid {
    grid-template-columns: 1fr 1fr;
  }
}

/* Card Styling */
.card {
  background: white;
  border-radius: 20px;
  padding: 2rem;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.15);
  animation: slideInUp 0.6s ease-out;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.card:hover {
  transform: translateY(-5px);
  box-shadow: 0 30px 80px rgba(0, 0, 0, 0.2);
}

.card-header {
  margin-bottom: 1.5rem;
  border-bottom: 2px solid #f0f4f8;
  padding-bottom: 1rem;
}

.card-header h2 {
  font-size: 1.5rem;
  margin: 0 0 0.5rem;
  color: #1a202c;
}

.card-subtitle {
  font-size: 0.9rem;
  color: #718096;
  margin: 0;
}

/* Upload Area */
.upload-area {
  border: 2px dashed #cbd5e1;
  border-radius: 16px;
  padding: 3rem 2rem;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s ease;
  background: #f8fafc;
}

.upload-area:hover {
  border-color: #667eea;
  background: #f0f4ff;
}

.upload-area.is-dragging {
  border-color: #667eea;
  background: #ede9fe;
  transform: scale(1.02);
}

.upload-icon {
  font-size: 3rem;
  margin-bottom: 1rem;
}

.upload-text {
  font-size: 1.1rem;
  font-weight: 600;
  color: #1a202c;
  margin: 0.5rem 0;
}

.upload-or {
  color: #718096;
  margin: 0.5rem 0;
  font-size: 0.9rem;
}

.upload-button {
  display: inline-block;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 0.75rem 1.5rem;
  border-radius: 10px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  margin-top: 0.5rem;
}

.upload-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 20px rgba(102, 126, 234, 0.3);
}

.upload-button input {
  display: none;
}

/* File Info */
.file-info {
  background: #f0f4f8;
  border-radius: 12px;
  padding: 1rem;
  margin: 1.5rem 0;
}

.info-item {
  display: flex;
  justify-content: space-between;
  padding: 0.5rem 0;
  font-size: 0.9rem;
}

.info-label {
  color: #718096;
  font-weight: 500;
}

.info-value {
  color: #1a202c;
  font-weight: 600;
}

/* Classify Button */
.classify-button {
  width: 100%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  padding: 1rem;
  border-radius: 12px;
  font-size: 1rem;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  margin-top: 1.5rem;
}

.classify-button:hover:not(:disabled) {
  transform: translateY(-3px);
  box-shadow: 0 15px 35px rgba(102, 126, 234, 0.4);
}

.classify-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.button-icon {
  font-size: 1.2rem;
}

.spinner {
  display: inline-block;
  width: 16px;
  height: 16px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-radius: 50%;
  border-top-color: white;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* Preview Section */
.preview-wrapper {
  display: flex;
  justify-content: center;
  padding: 2rem;
  background: #f8fafc;
  border-radius: 16px;
}

.preview-image {
  max-width: 100%;
  max-height: 400px;
  border-radius: 12px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
}

/* Result Section */
.result-section {
  grid-column: 1 / -1;
}

.success-card {
  background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%);
  border: 2px solid #86efac;
}

.success-header {
  border-bottom-color: #86efac;
  color: #15803d;
}

.result-content {
  display: grid;
  gap: 1.5rem;
}

.result-digit {
  text-align: center;
  padding: 2rem;
  background: white;
  border-radius: 16px;
  border: 2px solid #86efac;
}

.digit-display {
  font-size: 5rem;
  font-weight: 800;
  color: #667eea;
  margin: 0;
  line-height: 1;
}

.digit-label {
  margin: 1rem 0 0;
  color: #718096;
  font-size: 0.9rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.result-confidence {
  padding: 1.5rem;
  background: white;
  border-radius: 12px;
}

.confidence-bar {
  width: 100%;
  height: 12px;
  background: #e2e8f0;
  border-radius: 999px;
  overflow: hidden;
  margin-bottom: 0.5rem;
}

.confidence-fill {
  height: 100%;
  background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
  transition: width 0.6s ease;
}

.confidence-text {
  text-align: center;
  font-size: 1.3rem;
  font-weight: 700;
  color: #667eea;
  margin: 0;
}

.preprocessing-info {
  padding: 1rem;
  background: #f0f4f8;
  border-radius: 12px;
  font-size: 0.9rem;
  color: #1a202c;
}

/* Error Section */
.error-section {
  grid-column: 1 / -1;
}

.error-card {
  background: linear-gradient(135deg, #fef2f2 0%, #fee2e2 100%);
  border: 2px solid #fca5a5;
}

.error-header {
  border-bottom-color: #fca5a5;
  color: #b91c1c;
}

.error-content {
  padding: 1rem;
  background: white;
  border-radius: 12px;
  color: #7f1d1d;
}

/* Footer Info */
.footer-info {
  text-align: center;
  color: white;
  margin-top: 3rem;
  opacity: 0.9;
}

.footer-info p {
  margin: 0.5rem 0;
  font-size: 0.95rem;
}

.footer-info code {
  background: rgba(0, 0, 0, 0.2);
  padding: 0.3rem 0.6rem;
  border-radius: 6px;
  font-family: monospace;
}

/* Animations */
@keyframes slideInDown {
  from {
    opacity: 0;
    transform: translateY(-30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes slideInUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@media (max-width: 600px) {
  .digit-classifier {
    padding: 1rem;
  }

  .card {
    padding: 1.5rem;
  }

  .title {
    font-size: 1.8rem;
  }

  .digit-display {
    font-size: 3rem;
  }
}
</style>
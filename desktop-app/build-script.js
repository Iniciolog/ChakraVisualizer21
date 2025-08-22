const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

console.log('🚀 Начинаем сборку Kirlian Platform Desktop...');

// Проверяем наличие Node.js модулей
if (!fs.existsSync('./node_modules')) {
    console.log('📦 Устанавливаем зависимости...');
    execSync('npm install', { stdio: 'inherit' });
}

// Создаем папку dist если её нет
if (!fs.existsSync('./dist')) {
    fs.mkdirSync('./dist');
}

// Сборка для различных платформ
const platform = process.platform;

try {
    if (platform === 'win32') {
        console.log('🪟 Сборка для Windows...');
        execSync('npm run build-win', { stdio: 'inherit' });
        console.log('✅ Windows версия собрана успешно!');
    } else if (platform === 'darwin') {
        console.log('🍎 Сборка для Mac...');
        execSync('npm run build-mac', { stdio: 'inherit' });
        console.log('✅ Mac версия собрана успешно!');
    } else {
        console.log('🐧 Сборка для Linux...');
        execSync('npm run build', { stdio: 'inherit' });
        console.log('✅ Linux версия собрана успешно!');
    }
    
    // Показываем информацию о созданных файлах
    console.log('\n📁 Созданные файлы:');
    const distFiles = fs.readdirSync('./dist');
    distFiles.forEach(file => {
        const filePath = path.join('./dist', file);
        const stats = fs.statSync(filePath);
        const sizeInMB = (stats.size / (1024 * 1024)).toFixed(2);
        console.log(`   ${file} (${sizeInMB} MB)`);
    });
    
} catch (error) {
    console.error('❌ Ошибка при сборке:', error.message);
    process.exit(1);
}
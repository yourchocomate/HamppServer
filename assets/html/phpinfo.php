<?php
/**
 * HamppServer PHP Information Page
 * 
 * This file displays comprehensive PHP configuration information
 * in a clean, modern interface.
 */

// Security check - only allow access from localhost
$allowed_ips = ['127.0.0.1', '::1', 'localhost'];
$client_ip = $_SERVER['REMOTE_ADDR'] ?? $_SERVER['HTTP_X_FORWARDED_FOR'] ?? 'unknown';

if (!in_array($client_ip, $allowed_ips)) {
    http_response_code(403);
    die('Access denied: This page is only accessible from localhost');
}

?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PHP Information - HamppServer</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            margin: 0;
            padding: 2rem;
            min-height: 100vh;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 12px;
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
            overflow: hidden;
        }
        
        .header {
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            padding: 2rem;
            text-align: center;
        }
        
        .header h1 {
            margin: 0;
            font-size: 2.5rem;
            font-weight: 700;
        }
        
        .header p {
            margin: 0.5rem 0 0 0;
            opacity: 0.9;
            font-size: 1.1rem;
        }
        
        .content {
            padding: 2rem;
        }
        
        .navigation {
            margin-bottom: 2rem;
            display: flex;
            gap: 1rem;
            flex-wrap: wrap;
        }
        
        .nav-button {
            background: #f8f9fa;
            border: 2px solid #e9ecef;
            border-radius: 8px;
            padding: 0.8rem 1.5rem;
            text-decoration: none;
            color: #495057;
            font-weight: 500;
            transition: all 0.3s ease;
            cursor: pointer;
        }
        
        .nav-button:hover, .nav-button.active {
            background: #667eea;
            color: white;
            border-color: #667eea;
        }
        
        .section {
            display: none;
            margin-top: 2rem;
        }
        
        .section.active {
            display: block;
        }
        
        .back-link {
            display: inline-block;
            margin-bottom: 2rem;
            color: #667eea;
            text-decoration: none;
            font-weight: 500;
        }
        
        .back-link:hover {
            text-decoration: underline;
        }
        
        /* Override phpinfo styles */
        .phpinfo-content table {
            width: 100%;
            border-collapse: collapse;
            margin: 1rem 0;
        }
        
        .phpinfo-content th, 
        .phpinfo-content td {
            padding: 0.8rem;
            border: 1px solid #dee2e6;
            text-align: left;
        }
        
        .phpinfo-content th {
            background: #f8f9fa;
            font-weight: 600;
        }
        
        .phpinfo-content tr:nth-child(even) {
            background: #f8f9fa;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>PHP Information</h1>
            <p>HamppServer - PHP <?php echo PHP_VERSION; ?></p>
        </div>
        
        <div class="content">
            <a href="/" class="back-link">← Back to HamppServer</a>
            
            <div class="navigation">
                <button class="nav-button active" onclick="showSection('overview')">Overview</button>
                <button class="nav-button" onclick="showSection('full')">Full PHP Info</button>
                <button class="nav-button" onclick="showSection('modules')">Loaded Modules</button>
                <button class="nav-button" onclick="showSection('config')">Configuration</button>
            </div>
            
            <div id="overview" class="section active">
                <h2>PHP Overview</h2>
                <table>
                    <tr><th>PHP Version</th><td><?php echo PHP_VERSION; ?></td></tr>
                    <tr><th>PHP SAPI</th><td><?php echo php_sapi_name(); ?></td></tr>
                    <tr><th>Server Software</th><td><?php echo $_SERVER['SERVER_SOFTWARE'] ?? 'Unknown'; ?></td></tr>
                    <tr><th>Document Root</th><td><?php echo $_SERVER['DOCUMENT_ROOT'] ?? 'Unknown'; ?></td></tr>
                    <tr><th>Memory Limit</th><td><?php echo ini_get('memory_limit'); ?></td></tr>
                    <tr><th>Max Execution Time</th><td><?php echo ini_get('max_execution_time'); ?> seconds</td></tr>
                    <tr><th>Upload Max Filesize</th><td><?php echo ini_get('upload_max_filesize'); ?></td></tr>
                    <tr><th>Post Max Size</th><td><?php echo ini_get('post_max_size'); ?></td></tr>
                    <tr><th>Error Reporting</th><td><?php echo error_reporting(); ?></td></tr>
                    <tr><th>Display Errors</th><td><?php echo ini_get('display_errors') ? 'On' : 'Off'; ?></td></tr>
                </table>
            </div>
            
            <div id="full" class="section">
                <h2>Complete PHP Information</h2>
                <div class="phpinfo-content">
                    <?php
                    ob_start();
                    phpinfo();
                    $phpinfo = ob_get_clean();
                    
                    // Remove the HTML wrapper and just show the tables
                    $phpinfo = preg_replace('%^.*<body>(.*)</body>.*$%ms', '$1', $phpinfo);
                    echo $phpinfo;
                    ?>
                </div>
            </div>
            
            <div id="modules" class="section">
                <h2>Loaded PHP Modules</h2>
                <div style="columns: 3; column-gap: 2rem;">
                    <?php
                    $modules = get_loaded_extensions();
                    sort($modules);
                    foreach ($modules as $module) {
                        echo "<div style='margin-bottom: 0.5rem; break-inside: avoid;'>• " . htmlspecialchars($module) . "</div>";
                    }
                    ?>
                </div>
            </div>
            
            <div id="config" class="section">
                <h2>PHP Configuration</h2>
                <table>
                    <?php
                    $important_settings = [
                        'allow_url_fopen',
                        'allow_url_include',
                        'auto_prepend_file',
                        'auto_append_file',
                        'default_charset',
                        'default_mimetype',
                        'extension_dir',
                        'file_uploads',
                        'include_path',
                        'log_errors',
                        'max_input_time',
                        'open_basedir',
                        'session.save_handler',
                        'session.save_path',
                        'short_open_tag',
                        'upload_tmp_dir',
                        'user_agent',
                        'variables_order',
                    ];
                    
                    foreach ($important_settings as $setting) {
                        $value = ini_get($setting);
                        echo "<tr><th>" . htmlspecialchars($setting) . "</th><td>" . htmlspecialchars($value ?: 'Not set') . "</td></tr>";
                    }
                    ?>
                </table>
            </div>
        </div>
    </div>
    
    <script>
        function showSection(sectionId) {
            // Hide all sections
            const sections = document.querySelectorAll('.section');
            sections.forEach(section => section.classList.remove('active'));
            
            // Remove active from all buttons
            const buttons = document.querySelectorAll('.nav-button');
            buttons.forEach(button => button.classList.remove('active'));
            
            // Show selected section
            document.getElementById(sectionId).classList.add('active');
            
            // Mark button as active
            event.target.classList.add('active');
        }
    </script>
</body>
</html>

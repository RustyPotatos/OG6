<?php
if ($_SERVER["REQUEST_METHOD"] === "POST" && isset($_FILES["qrCode"])) {
    $uploadDir = "saved_qr_codes/";

    // Create directory if it doesn't exist
    if (!is_dir($uploadDir)) {
        mkdir($uploadDir, 0777, true);
    }

    $filePath = $uploadDir . basename($_FILES["qrCode"]["name"]);

    if (move_uploaded_file($_FILES["qrCode"]["tmp_name"], $filePath)) {
        echo "QR Code saved successfully: " . $filePath;
    } else {
        echo "Error saving QR Code.";
    }
} else {
    echo "Invalid request.";
}
?>

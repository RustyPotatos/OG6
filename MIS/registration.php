<?php
session_start();

$servername = "localhost";
$username = "Joslep101";
$password = "JoslepRESORT*1001";
$dbname = "tracom-proj-db";

// Establish Database Connection
$conn = new mysqli($servername, $username, $password, $dbname);
if ($conn->connect_error) {
    die("Connection Failed: " . $conn->connect_error);
}

if ($_SERVER["REQUEST_METHOD"] == "POST") {
    // Sanitize user input to prevent SQL injection
    $unit = trim($_POST['unit']);
    $rank = trim($_POST['rank']);
    $name = trim($_POST['name']);
    $afpsn = trim($_POST['afpsn']);
    $age = trim($_POST['age']);
    $email = trim($_POST['email']);
    $attendee = trim($_POST['attendee']);
    $cpnum = trim($_POST['cpnum']);

    // Validate required fields
    if (empty($unit) || empty($rank) || empty($name) || empty($afpsn) || empty($age) || empty($email) || empty($attendee) || empty($cpnum)) {
        die("Error: All fields are required!");
    }

    // Ensure valid email format
    if (!filter_var($email, FILTER_VALIDATE_EMAIL)) {
        die("Error: Invalid email format!");
    }

    // Save form data to session
    $_SESSION['form_data'] = $_POST;

    // Prepare SQL Insert Statement
    $stmt = $conn->prepare("INSERT INTO attendees (unit, rank, name, afpsn, age, email, attendee, cpnum) VALUES (?, ?, ?, ?, ?, ?, ?, ?)");
    $stmt->bind_param("ssssssss", $unit, $rank, $name, $afpsn, $age, $email, $attendee, $cpnum);

    if ($stmt->execute()) {
        $last_id = $conn->insert_id;
    
        // Generate QR Code Data in Row Format
        $qrData = "Unit: $unit | Rank: $rank | Name: $name | AFPSN: $afpsn | Age: $age | Email: $email | Attendee: $attendee | CP: $cpnum";
        $qrCodeURL = "https://api.qrserver.com/v1/create-qr-code/?size=150x150&data=" . urlencode($qrData);
    
        // Update QR Code in Database
        $updateSQL = "UPDATE attendees SET qr_code = ? WHERE id = ?";
        $updateStmt = $conn->prepare($updateSQL);
        $updateStmt->bind_param("si", $qrCodeURL, $last_id);
        
        if ($updateStmt->execute()) {
            // Store QR code in session
            $_SESSION['qr_code'] = $qrCodeURL;

            // Redirect to main.php with the QR code
            header("Location: main.php?qr=" . urlencode($qrCodeURL));
            exit();
        } else {
            echo "Error: Failed to update QR Code.";
        }

        $updateStmt->close();
    } else {
        echo "Error: Could not save data.";
    }

    $stmt->close();
}

$conn->close();
?>

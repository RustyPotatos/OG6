<?php
session_start();

// Clear QR code session on first visit
if (!isset($_GET['qr'])) {
    unset($_SESSION['qr_code']);
}
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="stylesheet" href="main.style.css">
    <link rel="icon" type="image/png" href="images/logo-with-bg-removebg-preview.png">
    <title>Event Registration</title>
</head>
<body>
    <section class="header">
        <nav>
            <a href="main.php"><img src="images/logo-with-bg-removebg-preview.png" alt="logo"></a>
        </nav>
    </section>

    <div class="form-wrapper">
        <div class="container">
            <h2>Registration</h2>
            <?php
            $formData = isset($_SESSION['form_data']) ? $_SESSION['form_data'] : [];
            ?>
            <form action="registration.php" method="post" id="registrationForm">
                <table>
                    <tr>
                        <td>Unit/Office</td>
                        <td><input type="text" name="unit" value="<?= htmlspecialchars($formData['unit'] ?? '') ?>" required></td>
                    </tr>
                    <tr>
                        <td>Rank</td>
                        <td><input type="text" name="rank" value="<?= htmlspecialchars($formData['rank'] ?? '') ?>" required></td>
                    </tr>
                    <tr>
                        <td>Name</td>
                        <td><input type="text" name="name" value="<?= htmlspecialchars($formData['name'] ?? '') ?>" required></td>
                    </tr>
                    <tr>
                        <td>AFPSN</td>
                        <td>
                            <input type="text" name="afpsn" value="<?= htmlspecialchars($formData['afpsn'] ?? '') ?>" required
                                onkeypress="return noSpaces(event)" oninput="removeSpaces(this)">
                        </td>
                    </tr>
                    <tr>
                        <td>Age</td>
                        <td><input type="number" name="age" value="<?= htmlspecialchars($formData['age'] ?? '') ?>" min="1" required></td>
                    </tr>
                    <tr>
                        <td>Email Address</td>
                        <td><input type="email" name="email" value="<?= htmlspecialchars($formData['email'] ?? '') ?>" required></td>
                    </tr>
                    <tr>
                        <td>Attendee</td>
                        <td><input type="text" name="attendee" value="<?= htmlspecialchars($formData['attendee'] ?? '') ?>" required></td>
                    </tr>
                    <tr>
                        <td>Cellphone Number</td>
                        <td><input type="text" name="cpnum" value="<?= htmlspecialchars($formData['cpnum'] ?? '') ?>" required></td>
                    </tr>
                </table>
                <div class="button-container">
                    <button type="button" class="clear-btn" onclick="clearForm()">Clear</button>
                    <button type="submit" class="register-btn">Register</button>
                </div>
            </form>
        </div>

        <div class="QR">
            <h2>QR CODE</h2>
            <?php
            // Get QR code from session or URL parameter
            $qrCodeURL = $_SESSION['qr_code'] ?? ($_GET['qr'] ?? "");

            // Store QR code in session if it comes from the URL
            if (!empty($_GET['qr'])) {
                $_SESSION['qr_code'] = $_GET['qr'];
            }
            ?>

            <div class="qr-frame">
                <?php if (!empty($qrCodeURL)): ?>
                    <img id="qrImage" src="<?php echo $qrCodeURL; ?>" alt="Generated QR Code">
                <?php else: ?>
                    <p>No QR Code Generated</p>
                <?php endif; ?>
            </div>

            <?php if (!empty($qrCodeURL)) { ?>
                <button id="saveQR" onclick="saveQRCode()">Save QR Code</button>
            <?php } ?>
        </div>
    </div>

    <script>

    async function saveQRCode() {
        let qrImage = document.getElementById("qrImage").src;
        let userName = document.querySelector("input[name='name']").value.trim();

        if (!userName) {
            alert("Please enter your name before saving the QR Code.");
            return;
        }

        userName = userName.replace(/[^a-zA-Z0-9_-]/g, "_"); // Remove special characters

        try {
            const response = await fetch(qrImage);
            const blob = await response.blob();

            if (window.showSaveFilePicker) {
                const fileHandle = await window.showSaveFilePicker({
                    suggestedName: `${userName}_QR_Code.png`,
                    types: [{ accept: { "image/png": [".png"] } }]
                });
                const writable = await fileHandle.createWritable();
                await writable.write(blob);
                await writable.close();
                alert("QR Code saved successfully!");
            } else {
                let url = window.URL.createObjectURL(blob);
                let link = document.createElement("a");
                link.href = url;
                link.download = `${userName}_QR_Code.png`;
                document.body.appendChild(link);
                link.click();
                document.body.removeChild(link);
                window.URL.revokeObjectURL(url);
            }
        } catch (error) {
            console.error("Error saving QR Code:", error);
            alert("Failed to save QR Code. Please try again.");
        }
    }


    function clearForm() {
        document.getElementById("registrationForm").reset();
        let inputs = document.querySelectorAll("#registrationForm input");
        inputs.forEach(input => input.value = '');
    }

    function noSpaces(event) {
        if (event.key === " ") {
            return false; // Prevent space key from being typed
        }
    }

    function removeSpaces(input) {
        input.value = input.value.replace(/\s/g, ''); // Remove spaces if pasted
    }

    </script>

</body>
</html>

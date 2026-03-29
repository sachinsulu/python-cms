<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no">
    <title>Online Booking</title>
    <script src="https://ajax.googleapis.com/ajax/libs/jquery/1.12.0/jquery.min.js"></script>
    <style>
        .loader {
            border: 10px solid #f3f3f3;
            border-top: 10px solid #3498db;
            border-radius: 50%;
            width: 30px;
            height: 30px;
            animation: spin 2s linear infinite;
            position: relative;
            left: 35%
        }

        @keyframes spin {
            0% {
                transform: rotate(0)
            }
            100% {
                transform: rotate(360deg)
            }
        }

        .main-load {
            position: fixed;
            top: 50%;
            left: 50%;
            -webkit-transform: translate(-50%, -50%);
            transform: translate(-50%, -50%);
            text-align: center
        }

        .main-load h2 {
            margin-bottom: 0
        }</style>
</head>
<body class="common">
<div id="hotel_result">

    <div class="main-load">
        <div class="loader"></div>
        <h2>Transaction Processing.</h2>
        <small>Please wait...</small>
    </div>

</div>
<script src="https://www.rojai.com/js/result.min.js"></script>
<!-- <script src="http://localhost/rojai/js/result.min.js"></script> -->

</body>
</html>
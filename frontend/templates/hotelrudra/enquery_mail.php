<?php
require_once("class.phpmailer.php");
// $usermail = User::get_UseremailAddress_byId(1);
$usermail = "sahas@longtail.info";
// $usermail = "info@bighotel.com.np";
$ccusermail = "support@longtail.info";
// $sitename = Config::getField('sitename', true);
$sitename = "Big Hotel";

foreach ($_POST as $key => $val) {
  $$key = $val;
}
if ($_POST['action'] == "forContact"):
    $body = '
        <table width="100%" border="0" cellpadding="0" style="font:12px Arial, serif;color:#222;">
            <tr>
                <td><p>Dear Sir,</p></td>
            </tr>
            <tr>
                <td>
                    <p>
                        <span style="font-size:14px; font-weight:bold">Contact message</span><br />
                        The details provided are:
                    </p>
                    <p>
                        <strong>Name</strong> : ' . $fullname . '<br />		
                        <strong>E-mail Address</strong>: ' . $email . '<br />
                        <strong>Address</strong>: ' . $address . '<br />
                        <strong>Phone</strong>: ' . $phone . '<br />
                        <strong>Message</strong>: ' . $message . '<br />
                    </p>
                </td>
            </tr>
            <tr>
                <td>
                    <p>Thank you,<br />
                    ' . $fullname . '
                    </p>
                </td>
            </tr>
        </table>
  ';
  
    $mail = new PHPMailer();
    $mail->SetFrom($email, $fullname);
    $mail->AddReplyTo($email, $fullname);
    $mail->AddAddress($usermail, $sitename);
    if (!empty($ccusermail)) {
        $rec = explode(';', $ccusermail);
        if ($rec) {
            foreach ($rec as $row) {
                $mail->AddCC($row, $sitename);
            }
        }
    }
  
    $mail->Subject = 'Contact mail from from ' . $fullname;
    $mail->MsgHTML($body);
  
    if (!$mail->Send()) {
        echo json_encode(array("action" => "unsuccess", "message" => "We could not sent your message at the time. Please try again later."));
    } else {
        echo json_encode(array("action" => "success", "message" => "Your message has been successfully sent."));
    }
  endif;
  

if ($_POST['action'] == "forHall"):
  $body = '
      <table width="100%" border="0" cellpadding="0" style="font:12px Arial, serif;color:#222;">
          <tr>
              <td><p>Dear Sir,</p></td>
          </tr>
          <tr>
              <td>
                  <p>
                      <span style=" font-size:14px; font-weight:bold">Hall Inquiry message</span><br />
                      The details provided are:
                  </p>
                  <p>		
                      <strong>Name</strong> : ' . $name . '<br />		
                      <strong>E-mail Address</strong>: ' . $email . '<br />
                      <strong>Phone</strong>: ' . $phone . '<br />
                      <strong>Event Name</strong>: ' . $event_name . '<br />
                      <strong>Event Date</strong>: ' . $event_date . '<br />
                      <strong>Pax</strong>: ' . $pax . '<br />
                      <strong>Event Detail</strong> : ' . $message . '<br />		
                  </p>
              </td>
          </tr>
          <tr>
              <td>
                  <p>Thank you,<br />
                  ' . $name . '
                  </p>
              </td>
          </tr>
      </table>
';

  $mail = new PHPMailer();
  $mail->SetFrom($email, $name);
  $mail->AddReplyTo($email, $name);
  $mail->AddAddress($usermail, $sitename);
  if (!empty($ccusermail)) {
      $rec = explode(';', $ccusermail);
      if ($rec) {
          foreach ($rec as $row) {
              $mail->AddCC($row, $sitename);
          }
      }
  }

  $mail->Subject = 'Hall Inquiry mail from ' . $name;
  $mail->MsgHTML($body);

  if (!$mail->Send()) {
      echo json_encode(array("action" => "unsuccess", "message" => "We could not sent your Inquiry at the time. Please try again later."));
  } else {
      echo json_encode(array("action" => "success", "message" => "Your Inquiry has been successfully sent."));
  }
endif;


?>
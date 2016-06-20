<?php
    $dir = '../../src/testing/';
    $execFile = './search.py';
    $shell = './search.sh';

    $type = $_POST['type'];
    if($type == 'file') {
        $file = $_FILES;
        $tmp_name = $file['file']['tmp_name'];

        // exec python then produce a result file
        $command = $shell.' '.$dir.' '.$execFile.' '.$type.' '.$tmp_name;
        $output = shell_exec($command);

        // read file
        $file = $dir.'answer_demonic.json';
        $fp = fopen($file, 'r');
        $result = json_decode(fread($fp, filesize($file)));
        fclose($fp);

        echo json_encode($result);
    } else if($type == 'string') {

    }
?>

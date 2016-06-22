<?php
    /* This File Is Just A MiddleWare To Call Python
    *
    *  */
    $dir = '../../src/testing/';
    $pythonFile = './search.py';
    $shellFile = './search.sh';

    // Build The Command String
    $type = $_POST['type'];
    if($type == 'file') {
        $file = $_FILES;
        $name = '/tmp/'.$file['file']['name'];
        $tmp_name = $file['file']['tmp_name'];
        rename($tmp_name, $name);

        $command = $shellFile.' '.$dir.' '.$pythonFile.' '.$type.' '.$name;
    } else if($type == 'string') {
        $request = $_POST['string'];

        $command = $shellFile.' '.$dir.' '.$pythonFile.' '.$type.' '.$request;
    }

    // Exec The Command
    $output = shell_exec($command);
    // read file
    $file = $dir.'answer_demonic.json';
    $fp = fopen($file, 'r');
    $result = json_decode(fread($fp, filesize($file)));
    fclose($fp);

    echo json_encode($result);
?>

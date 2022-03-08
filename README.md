
<h2>
    <ul>
    <li> Python 3.10 </li>
    <li> Virtualbox </li>
    <li> Windows | GNU/Linux </li>
    </ul>
</h2>

<h3>
I often found myself manually updating my ~/.ssh/config file for different bridged vms (Virtualbox).</br>

This turned out to be tedious.
</h3>

<h4>
This simple tool is supposed to find the fresh ip of your VM (by name)</br> 
and update the entry of ~/.ssh/config for this name (case insensitive).</br>
It assumes that you have the `VBoxManage` binary available in your path.</br>
If the binary fails the script will Raise an Exception.
</h4>

<br/>

<h3>
How to run the script? <br/>
</h3>

</br>
Simply invoke:

- ```python config.py``` # interactive shell
- ```python config.py "$some_vm_name"```

Clipboard for the lazies:  

    python config.py

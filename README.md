# Julabo library

![Julabo CF31](docs/cf31.png)

This library is used to control basic features of Julabo equipment. It is
composed of a core library, an optional simulator and an optional
[tango](https://tango-controls.org/) device server.

It has been tested with CF31, HL-4 and FC models, but should work with
other models too.

It can be used with either with a direct serial line (read below
on the recommended way to setup a serial line connection) or remotely
through TCP socket (either raw socket or rfc2217). In the latter case
the master device to which the Julabo serial line is connected must
provide a raw socket or rfc2217 interface.

## Installation

From within your favorite python environment type:

`$ pip install julabo`


## Library

The core of the julabo library consists of JulaboCF, JulaboHL and JulaboFC
objects.
To create a Julabo object you need to pass a communication object.
Here is how to connect to a julabo CF31 through a raw tcp socket:

```python

from julabo import JulaboCF, connection_for_url


async def main():
    conn = connection_for_url("tcp://controls.lab.org:17890")
    dev = JulaboCF(conn)
    await conn.open()

    ident = await dev.identification()
    status = await dev.status()
    print(f"{ident} status is: {status}")

    # read temperature:
    temp = await dev.bath_temperature()
    print(f"Bath temperature: {temp} degC")

    # start the device
    started = await dev.is_started()
    if not started:
       await cryo.start()

    # define a new set point
    await dev.set_point_1(34.56)

asyncio.run(main())
```

#### Serial line

To access a serial line based Julabo device it is strongly recommended you spawn
a serial to tcp bridge using [ser2net](https://linux.die.net/man/8/ser2net),
[ser2sock](https://github.com/tiagocoutinho/ser2sock) or
[socat](https://linux.die.net/man/1/socat)

Assuming your device is connected to `/dev/ttyS0` and the baudrate is set to 9600,
here is how you could use socat to expose your device on the machine port 5000:

`socat -v TCP-LISTEN:5000,reuseaddr,fork file:/dev/ttyS0,rawer,b9600,cs8,eol=10,icanon=1`

It might be worth considering starting socat, ser2net or ser2sock as a service using
[supervisor](http://supervisord.org/) or [circus](https://circus.rtfd.io/).

### Simulator

A Julabo simulator is provided.

Before using it, make sure everything is installed with:

`$ pip install julabo[simulator]`

The [sinstruments](https://pypi.org/project/sinstruments/) engine is used.

To start a simulator you need to write a YAML config file where you define
how many devices you want to simulate and which properties they hold.

The following example exports 1 hardware device with a minimal configuration
using default values:

```yaml
# config.yml

devices:
- class: JulaboCF
  package: julabo.simulator
  transports:
  - type: serial
    url: /tmp/julabo-cf31
    baudrate: 9600
```

To start the simulator type:

```terminal
$ sinstruments-server -c ./config.yml --log-level=DEBUG
2020-09-01 21:04:43,172 INFO  simulator: Bootstraping server
2020-09-01 21:04:43,173 INFO  simulator: no backdoor declared
2020-09-01 21:04:43,173 INFO  simulator: Creating device JulaboCF ('JulaboCF')
2020-09-01 21:04:43,186 INFO  simulator: Created symbolic link "/tmp/julabo-cf31" to simulator pseudo terminal '/dev/pts/4'
2020-09-01 21:04:43,186 INFO  simulator.JulaboCF[/tmp/julabo-cf31]: listening on /tmp/julabo-cf31 (baud=9600)

```

(To see the full list of options type `sinstruments-server --help`)

You can access it as you would a real hardware. Here is an example using python
serial library on the same machine as the simulator:

```python
$ python
>>> from julabo import JulaboCF, connection_for_url
>>> conn = connection_for_url("serial:///tmp/julabo-cf31", concurrency="syncio")
>>> dev = JulaboCF(conn)
>>> conn.open()
>>> print(dev.identification())
JULABO CRYOCOMPACT CF31 VERSION 5.0
```

### Tango server

A [tango](https://tango-controls.org/) device server is also provided.

Make sure everything is installed with:

`$ pip install julabo[tango]`

Register a julabo tango server in the tango database:
```
$ tangoctl server add -s Julabo/test -d JulaboCF test/julabo/1
$ tangoctl device property write -d test/julabo/1 -p url -v "tcp://controls.lab.org:17890"
```

(the above example uses [tangoctl](https://pypi.org/project/tangoctl/). You would need
to install it with `pip install tangoctl` before using it. You are free to use any other
tango tool like [fandango](https://pypi.org/project/fandango/) or Jive)

Launch the server with:

```terminal
$ Julabo test
```

## TODO

* Add `on_connection_made` callback to initialize controller with:
  * support for async local serial line connection
  * cache identification()

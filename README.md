# Keypad Racer

An game for [PyWeek 32].

*The racetrack loops: it is **neverending**.*

This turn-based racing game is a recreation of a pen-and-paper game
I enjoyed back at school.

[PyWeek 32]: https://pyweek.org/32/


## Requirements

The game needs:
* Python 3.9 (older versions not tested)
* OpenGL 3.3+
* `moderngl`, as an OpenGL abstraction
* `pyglet`, for creating a window and handling events
* `pypng`, for reading images

Install these requirements (preverably in a virtual environment) using:

    $ python -m pip install -r requirements.txt

(Compiled wheels for the dependencies should be available for Linux, Windows
and Mac; on other platforms you'll probably need a compiler and headers.)


## Running the game

Run the game with the traditional PyWeek command:

    $ python game.py

The game will save a file called `keypad_racer.conf` into the
current directory.
(You can remove it to run the tutorial again.)


## Gameplay

The game starts with a tutorial – go through it!

Here's what it doesn't teach:

* Keyboard mappings can be changed by HOLDING a button on the screen
  with a MOUSE, and pressing the desired key.


## The controls

Each player needs 9 keys, ideally in a grid.
The best way to play is on a grid – a numeric keypad:

    ┏━━━━━━━┳━━━━━━━┳━━━━━━━┓
    ┃       ┃       ┃       ┃
    ┃   7   ┃   8   ┃   9   ┃
    ┃       ┃       ┃       ┃
    ┣━━━━━━━╋━━━━━━━╋━━━━━━━┫
    ┃       ┃       ┃       ┃
    ┃   4   ┃   5   ┃   6   ┃
    ┃       ┃       ┃       ┃
    ┣━━━━━━━╋━━━━━━━╋━━━━━━━┫
    ┃       ┃       ┃       ┃
    ┃   1   ┃   2   ┃   3   ┃
    ┃       ┃       ┃       ┃
    ┗━━━━━━━┻━━━━━━━┻━━━━━━━┛

If you don't have one and/or want to play with friends,
share a keyboard -- there are enough keys for 3 people. By default they are:

        Player 1        Player 2        Player 3
     ┏━━━┳━━━┳━━━┓   ┏━━━┳━━━┳━━━┓   ┏━━━┳━━━┳━━━┓
     ┃ Q ┃ W ┃ E ┃   ┃ T ┃ Y ┃ U ┃   ┃ O ┃ P ┃ [ ┃
     ┗┳━━┻┳━━┻┳━━┻┓  ┗┳━━┻┳━━┻┳━━┻┓  ┗┳━━┻┳━━┻┳━━┻┓
      ┃ A ┃ S ┃ D ┃   ┃ G ┃ H ┃ J ┃   ┃ L ┃ ; ┃ ' ┃
      ┗┳━━┻┳━━┻┳━━┻┓  ┗┳━━┻┳━━┻┳━━┻┓  ┗┳━━┻┳━━┻┳━━┻━━━━━━┓
       ┃ Z ┃ X ┃ C ┃   ┃ B ┃ N ┃ M ┃   ┃ . ┃ / ┃ R Shift ┃
       ┗━━━┻━━━┻━━━┛   ┗━━━┻━━━┻━━━┛   ┗━━━┻━━━┻━━━━━━━━━┛

Thing will get quite crowded with 3 players, unless you plug in several
keyboards. Be careful not to press another player's keys!

(Note that on some systems there's significant lag when typing on several
keyboards a once.)

Hidden option: if you put `dvorak` in the `settings.conf` file,
you'll start with a Dvorak keyboard layout.


## What's there to see

Accelerate, decelerate, try to get to the finish, another lap, repeat.
The racetrack loops, so it is **neverending** ;)


## Licence & Credits

TL;DR:

* This Game: Petr Viktorin
* Crash sound by Michel Baradari
* Fonts:
  * [Gemunu Libre] by *mooniak*.
  * Additional symbols from [M PLUS 1p] by Coji Morishita & M+ Fonts Project
* MSDF font generator: [msdfgen] by Viktor Chlumský
* The racetrack is based on [Masaryk circuit], a racetrack in my home town.
* Shader ideas and snippets:
  * Nicolas P. Rougier
  * Íñigo Quílez

Long story:

### Game

The code is available under this MIT licence:

> Copyright © 2021 Petr Viktorin
>
> Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
>
> The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
>
> THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

### Sound

The crash sound is from *9 sci-fi computer sounds and beeps*
by Michel Baradari, used under the [CC-BY 3.0] lcense.

[beeps]: https://opengameart.org/content/9-sci-fi-computer-sounds-and-beeps
[CC-BY 3.0]: https://creativecommons.org/licenses/by/3.0/

### Racetrack

The racetrack is based (maybe too closely) on the [Masaryk circuit],
a racetrack in my home town.

[Masaryk circuit]: https://en.wikipedia.org/wiki/Brno_Circuit


### Font

The font used is [Gemunu Libre] by *mooniak*.

[Gemunu Libre]: https://github.com/mooniak/gemunu-libre-font/releases/tag/1.001

Additional symbols were taken from [M PLUS 1p] by Coji Morishita & M+
Fonts Project.

[M PLUS 1p]: https://fonts.google.com/specimen/M+PLUS+1p

Both fonts are unter the OFL licence (included in the source only;
font files aren't used in the game).

The font was preprocessed with [msdfgen] by Viktor Chlumský.

[msdfgen]: https://github.com/Chlumsky/msdfgen

### Shaders

The game incorporates several techniques and code examples from
Nicolas P. Rougier's book *Python & OpenGL for Scientific Visualization*,
available at https://www.labri.fr/perso/nrougier/python-opengl
– these are under this BSD license:

> Copyright (c) 2017, Nicolas P. Rougier
> All rights reserved.
>
> Redistribution and use in source and binary forms, with or without
> modification, are permitted provided that the following conditions are met:
>
> 1. Redistributions of source code must retain the above copyright notice, this
>    list of conditions and the following disclaimer.
>
> 2. Redistributions in binary form must reproduce the above copyright notice,
>    this list of conditions and the following disclaimer in the documentation
>    and/or other materials provided with the distribution.
>
> THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
> ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
> WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
> DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
> FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
> DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
> SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
> CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
> OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
> OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.


Some shaders were taken or adapted from Íñigo Quílez's collection at
https://iquilezles.org/www/articles/distfunctions2d/distfunctions2d.htm
– under this MIT licence:

> Copyright © 2018 Inigo Quilez
>
> Copyright © 2019 Inigo Quilez
>
> Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions: The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software. THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

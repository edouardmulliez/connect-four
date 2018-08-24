# Install requiered packages
brew install mercurial sdl sdl_image sdl_mixer sdl_ttf portmidi

# # to play sounds - not working finally
# brew install gst-plugins-bad

# Install smpeg package via another brew tap
brew tap homebrew/headonly
brew install smpeg

# Install cython
export CFLAGS="-arch i386 -arch x86_64"
export FFLAGS="-m32 -m64"
export LDFLAGS="-Wall -undefined dynamic_lookup -bundle -arch i386 -arch x86_64"
export CC=gcc
export CXX="g++ -arch i386 -arch x86_64"
pip install -I Cython==0.27.3

# Install pygame
hg clone https://bitbucket.org/pygame/pygame
cd pygame
python setup.py build
python setup.py install
cd ..
rm -rf pygame

# Install kivy
git clone https://github.com/kivy/kivy
cd kivy
python setup.py install
cd ..
rm -rf kivy


# SCGv8
# Kay Johnston

# Added HR and Age-Mass diagram outputs.
# Added flags for catalogue, not primary and incomplete entries.

# Areas of concern;

# Major problem with old data sets: FD implemented something which changed the ages of systems.
# This has stopped stars being unfeasibly old, but changed all the values!
# The change looks to have happened with patch 1.3 so any age data from 1.2 and earlier is suspect.

# A7 IAB / A7 IB boundary.  The luminosity classes are reversed.
# B9 IA / IAB boundary.  The luminosity classes are reversed.

# B3 VA, B4 VI, B7 IVA; how do we distinguish these from B0 VZ of equivalent age and mass?
# Generally these stars are at high luminosity and radius for their age, but not so much as to stand out.
# B3 VA may have higher relative pressure (>~4.5) than equivalent B0 VZ.

# Discrimination between different types of Wolf-Rayet.
# We can distinguish between WC univerally < 60Msol, WO universally > 60Msol
# However, WN and WNC are spread all over.
# No obvious luminosity correlations.

# Discrimination between different types of Carbon star.
# (To some degree we can separate out CN, CJ from MS and S, as the CN and CJ are cool.)
# Added some limited handling for higher mass C stars.

# Discrimination between different types of white dwarf.
# DC are generally cooler than DA, but it's not exact.
# Additionally can't distinguish the variables.

# Ok, need more data and a lot of work on sorting out the exact boundaries, but this is pretty much right.

# Adding an output display.
from PIL import Image, ImageDraw
import math

class Star():
    def __init__(self,name,mass,radius,temperature,age):
        self.name = name
        self.mass = mass
        self.radius = radius
        self.temperature = temperature
        self.rel_luminosity = (self.radius**2) * ((self.temperature/5778)**4)
        self.rel_pressure = ((self.temperature/5778)**4) / (self.mass**2)
        self.age = age
        self.source = 'not set'

    def report(self):
        print(self.name,self.mass,self.radius,self.temperature,self.age,'r. lum.',self.rel_luminosity,'r. pr.',round(self.rel_pressure,3))

class Boundary():
    def __init__(self,name,lum_lo,lum_hi):
        # name - the luminosity class
        # lum_lo, lum_hi - lower and upper relative (L/Lsol) luminosity boundaries
        self.name = name
        self.lum_lo = lum_lo
        self.lum_hi = lum_hi

    def report(self):
        print(self.name,self.lum_lo,self.lum_hi)

class Division():
    def __init__(self,colour,subdiv,t_lo,t_hi):
        # colour - temperature colour
        # subdiv - subdivision
        # t_lo, t_hi - lower and upper temperature boundaries, Kelvin
        self.colour = colour
        self.subdiv = subdiv
        self.t_lo = t_lo
        self.t_hi = t_hi
        self.boundaries = []

    def report(self):
        print(self.colour,self.subdiv,self.t_lo,self.t_hi)
        for boundary in self.boundaries:
            boundary.report()

def read_boundary_file(filename):
    division_list = []
    with open(filename, 'r') as opened:
        readtext = opened.read()
    lines = readtext.split('\n')
    for line in lines:
        sl = line.split(',')
        if sl[0] != '':
            try:
                colour = str(sl[0])
                try:
                    subdiv = int(sl[1])
                except:
                    subdiv = 0
                t_lo = int(sl[2])
                t_hi = int(sl[3])
                newdivision = Division(colour,subdiv,t_lo,t_hi)
                # Not ideal, but it works well enough.
                pos = 4
                for expected in expected_boundaries:
                    if sl[pos] != '':
                        name = expected
                        lum_lo = float(sl[pos])
                        lum_hi = float(sl[pos+1])
                        lum_lo = round(lum_lo,4)
                        lum_hi = round(lum_hi,4)
                        newdivision.boundaries.append(Boundary(name,lum_lo,lum_hi))
                    pos += 2
                division_list.append(newdivision)
            except:
                print('failed')
    return division_list

def read_star_list(filename):
    starList = []
    with open(filename, 'r') as opened_file:
        readtext = opened_file.read()
    readtext = str(readtext)
    splittext = readtext.split('\n')
    for newline in splittext:
        line = newline.split(',')
        try:
            mass = float(line[7])
            radius = float(line[8])
            temperature = int(line[9])
            age = int(line[10])
            colour = line[11]
            source = line[14]
            try:
                subdiv = int(line[12])
                luminosity = line[13]
            except:
                subdiv = 0
                luminosity = 'undetermined'
            if colour not in remnants:
                name = colour + str(subdiv) + ' ' + luminosity
            else:
                name = colour
            if source == 'cat':
                name += ' (catalogue star)'
            newStar = Star(name,mass,radius,temperature,age)
            newStar.source = source
            starList.append(newStar)
        except:
            if newline != '':
                print('Failed to parse:',newline)
    return starList

def guess(mass,radius,temperature,age):
    # This could be moved into a star class.
    luminosity = (radius**2) * ((temperature/5778)**4)
    pressure = ((temperature/5778)**4) / (mass**2)
    g_colour = ''
    g_subdiv = ''
    g_luminosity = ''
    a_subdiv = ''
    a_luminosity = ''
    # Go through main list of divisions and find one that fits.
    # As this is only empirical and hasn't been fitted exactly, there are big gaps.
    for division in division_list:
        if temperature >= division.t_lo and temperature <= division.t_hi:
            g_colour = division.colour
            for boundary in division.boundaries:
                if luminosity >= boundary.lum_lo and luminosity <= boundary.lum_hi:
                    g_subdiv = str(division.subdiv)
                    a_subdiv = g_subdiv # Adding this to record the originally assigned value in case g_subdiv changes.
                    g_luminosity = boundary.name
                    a_luminosity = g_luminosity # Adding this to record the originally assigned value in case g_luminosity changes.
                    
    # Handle protostars and young stars.
    # Not working right yet.
    # T-Tauris
    # Upper mass bound is given by the 'Ace' line.
    ace = 4.6 * (age**-0.3)
    # Upper age bound is at the 'Baron' line, 210 MYr.
    baron = 210
    if age <= baron and mass <= ace:
        if mass <= 3:
            # A TTS which would become a brown dwarf gets a 'VI' classification.
            # Not sure if this is universally true but it certainly works in all tried cases.
            if g_colour in brown_dwarfs:
                g_colour = 'TTS'
                g_luminosity = 'VI'
            else:
                g_colour = 'TTS'
    # Check for young VZ stars
    # Upper mass bound is given by the 'Pumpkin' line.
    # Is this right?
    pumpkin = 55 * (age**-0.4)
    # Upper age bound is below the 'Snoopy' line, 240 MYr.
    snoopy = 240
    # Check if it fits within these but not within the TTS box.
    if age < snoopy and mass <= pumpkin and g_colour != 'TTS':
        # Check that it's not a giant or subgiant (to catch the O and B stars.)
        if radius <= 11:
            if age == 2:
                if radius <= 3:
                    g_colour = 'Ae/Be'
                else:
                    g_subdiv = 0
                    g_luminosity = 'VZ'
            else:
                g_subdiv = 0
                g_luminosity = 'VZ'
    # Try to catch unusual B stars:
    # This works for the pair of B3 VAs in the sample, but perhaps isn't really true.
    # I suspect it's a slope instead of a straight line in any case.  Need more data!
    if g_colour == 'B' and g_luminosity == 'VZ' and age > 40:
        if pressure > 5:
            g_subdiv = a_subdiv
            g_luminosity = a_luminosity
    # Check for Herbigs
    # We can distinguish them from equivalent mass VZ stars by their radius.
    # In reality, the Herbig radius would be larger; in the Forge, it's much smaller.
    # I'm going to go with a 3 solar radius cutoff, though it's probably much lower.
    # And try to pick up those Herbigs which are still over the Pumpkin line.
    # Final Herbig check.
    if age == 2:
        if mass > pumpkin and radius <=3:
            g_colour = 'Ae/Be'
    
    # Handle stellar remnants
    # Neutron stars and black holes can be distinguished by temperature.
    if temperature >= 70000:
        g_colour = 'NS'
        g_subdiv = ''
        g_luminosity = ''
    elif temperature == 0:
        g_colour = 'BH'
        g_subdiv = ''
        g_luminosity = ''
    # White dwarf handling isn't complete.
    if radius > 0.005 and radius < 0.03:
        g_colour = 'D??'
        g_subdiv = '0'
        g_luminosity = 'VII'
        # This boundary isn't absolute, but it's a reasonable approximation that the cooler dwarfs are DC and the hotter ones largely DA.
        # Needs more work though to get something which is properly predictive.
        # Not sure if the age boundary is absolute, it might be.
        # Not sure whether the mass boundary helps, or even exists, but it looks like it might.
        if temperature <= 9000 and age > 9500 and mass > 0.375:
            g_colour = 'DC'
        else:
            g_colour = 'DA'
        
    # Need something to handle Wolf-Rayets.
    # Increased mass boundary to 42.
    if age == 1 and mass >= 42 and radius <= 10:
        # Leaving aside the distinction between WN, WNC, WC on the one hand and WO on the other.
        # This gives false positive identifications.  A result of WC indicates WN,WNC,WC; WO indicates WN,WNC,WO.
        # Need more data and checks here.
        if mass <= 60:
            if temperature > 10000:
                g_colour = 'WC'
                g_subdiv = 0
                g_luminosity = 'I'
            # There's a small group of low-temperature stars that are of all types (except WO?)
            # And the majority are probably WN.  Not certain; this fits the data I have so far.
            # But this is just saying that it's more probable, not a definite assignment.
            else:
                g_colour = 'WN'
                g_subdiv = 0
                g_luminosity = 'I'
        else:
            g_colour = 'WO'
            g_subdiv = 0
            g_luminosity = 'I'

    # Attempt to identify some of the carbon stars.
    # Fifi line marks a boundary above which the only stars are C.  Should check if possible to separate CN from CJ.
    fifi = 42.7 * (age**-0.4)
    # A lower line at mass = 42.25 * (age**-0.4) marks a boundary above which M giants are either very rare or nonexistent, and only
    # evolved MS, S, C remain.  Can't distinguish MS from S from the looks of things though.
    # Temperature/age is mixed.  Mass/age is mixed.
    if g_colour == 'M' and age > 12300 and mass > fifi and 'III' in g_luminosity:
        g_colour = 'CN'

    return g_colour,g_subdiv,g_luminosity

# Draws a rough HR diagram given a list of stars.
# Lots of hand-coded values in there and it assumes we always start from temperature 0.
# Could expand to target a particular box of temperature and luminosity values.
def HR_diagram(starList,picsize):
    # Size of the output image in pixels.
    xdim,ydim = picsize
    # Ranges of the axes in K and in units of L/Lsol.
    xmin = 0
    xmax = 70000
    ymin = 1e-6
    ymax = 1e8
    yminlog = math.log(ymin,10)
    ymaxlog = math.log(ymax,10)
    yoverall = ymaxlog - yminlog
    # Create new blank HR diagram image.
    size = (xdim,ydim)
    HR = Image.new('RGB',size)
    draw = ImageDraw.Draw(HR)
    # Go through the stars in the starlist plotting them onto the diagram.
    for star in starList:
        if star.temperature <= xmax:
            x = star.temperature
        else:
            x = xmax
        y = star.rel_luminosity
        xpos = x
        if y > 0:
            ypos = math.log(y,10) - yminlog
        else:
            ypos = 0
        xfin = xdim - int((x/xmax) * xdim)
        yfin = int((ypos/yoverall) * ydim)
        pos = (xfin,yfin)
        col = (255,255,255)
        c_size = 2
        if 'O' in star.name[0:1]:
            col = (0,0,255)
        elif 'B' in star.name[0:1]:
            col = (127,127,255)
        elif 'A' in star.name[0:1] or 'D' in star.name[0:1]:
            col = (255,255,255)
            if 'D' in star.name[0:1]:
                c_size = 1
        elif 'F' in star.name[0:1]:
            col = (255,255,127)
        elif 'G' in star.name[0:1]:
            col = (255,255,0)
        elif 'K' in star.name[0:1]:
            col = (255,127,0)
        elif 'M' in star.name[0:1] or 'S' in star.name[0:1]:
            col = (255,0,0)
        elif 'L' in star.name[0:1] or 'C' in star.name[0:1]:
            col = (153,0,0)
        elif 'T' in star.name[0:1]:
            col = (153,76,0)
        elif 'Y' in star.name[0:1]:
            col = (153,0,153)
        elif 'W' in star.name[0:1]:
            col = (255,127,255)
            c_size = 1
        if 'Ae' in star.name[0:2]:
            col = (255,255,127)
            c_size = 1
        if 'TTS' in star.name[0:3]:
            col = (255,127,63)
            c_size = 1
        try:
            epos = [(xfin-c_size,yfin-c_size),(xfin+c_size,yfin+c_size)]
            # Draws only trusted, proc-gen stars.
            if star.source not in known_bad:
                draw.ellipse(epos,fill=col,outline=col)
        except:
##            print('failed to plot at',pos)
##            star.report()
            alice = 'do nowt'
    HR = HR.transpose(Image.FLIP_TOP_BOTTOM)
    return HR

def AM_diagram(starList,picsize,bounds):
    # Size of the output image in pixels.
    xdim,ydim = picsize
    # Ranges of the axes in K and in units of L/Lsol.
    xmin,ymin,xmax,ymax = bounds
    # Calculate log boundary values.
    xminlog = math.log(xmin,10)
    xmaxlog = math.log(xmax,10)
    xoverall = xmaxlog - xminlog
    yminlog = math.log(ymin,10)
    ymaxlog = math.log(ymax,10)
    yoverall = ymaxlog - yminlog
    # Create new working image.
    size = (xdim,ydim)
    AM = Image.new('RGB',size)
    draw = ImageDraw.Draw(AM)
    # Go through the list of stars drawing them onto the new image.
    for star in starList:
        x = star.age
        y = star.mass
        # Correct to progenitor mass for stellar remnants.
        if star.name[0] == 'D':
            y *= 2.5
        elif star.name[0:2] == 'NS' or star.name[0:2] == 'BH':
            y *= 2
        if x > 0:
            xpos = math.log(x,10) - xminlog
        else:
            xpos = 0
        if y > 0:
            ypos = math.log(y,10) - yminlog
        else:
            ypos = 0
        xfin = int((xpos/xoverall) * xdim)
        yfin = int((ypos/yoverall) * ydim)
        pos = (xfin,yfin)
        col = (255,255,255)
        c_size = 2
        if star.name[0] == 'O':
            col = (0,0,255)
        elif 'B' in star.name[0:1]:
            col = (127,127,255)
        elif 'A' in star.name[0:1] or 'D' in star.name[0:1]:
            col = (255,255,255)
            if 'D' in star.name[0:1]:
                c_size = 1
        elif 'F' in star.name[0:1]:
            col = (255,255,127)
        elif 'G' in star.name[0:1]:
            col = (255,255,0)
        elif 'K' in star.name[0:1]:
            col = (255,127,0)
        elif 'M' in star.name[0:1] or 'S' in star.name[0:1]:
            col = (255,0,0)
        elif 'L' in star.name[0:1] or 'C' in star.name[0:1]:
            col = (153,0,0)
        elif 'T' in star.name[0:1]:
            col = (153,76,0)
        elif 'Y' in star.name[0:1]:
            col = (153,0,153)
        elif 'W' in star.name[0:1]:
            col = (255,127,255)
            c_size = 1
        if 'Ae' in star.name[0:2]:
            col = (255,255,127)
            c_size = 1
        if 'TTS' in star.name[0:3]:
            col = (255,127,63)
            c_size = 1
        if 'BH' in star.name[0:2]:
            col = (31,31,31)
        if 'NS' in star.name[0:2]:
            col = (255,255,255)
            c_size = 1
        try:
            epos = [(xfin-c_size,yfin-c_size),(xfin+c_size,yfin+c_size)]
            # Draws only trusted, proc-gen stars.
            if star.source not in known_bad:
                draw.ellipse(epos,fill=col,outline=col)
        except:
            print('failed')
    AM = AM.transpose(Image.FLIP_TOP_BOTTOM)
    return AM
    

# Lists used for reading boundaries, for conditional guessing and sorting.
expected_boundaries = ['IAO','IA','IAB','IB','IIA','IIAB','IIB','IIIA','IIIAB','IIIB','IVA','IVAB','IVB','VA','VAB','VB','VI','V','None']
brown_dwarfs = ['L','T','Y']
remnants = ['BH','NS']
known_bad = ['cat','cat/ha','not primary','incomplete']

print('Reading boundary and star list files.')
print()

# Read the list of boundaries.
filename = 'empirical.csv'
division_list = read_boundary_file(filename)

# Read a list of stars.
filename = 'starlist13.csv'
starList = read_star_list(filename)

fails = 0
ignored = 0

print()
print('Going through list of stars.')
print()

# Go through stars checking if the guess matches the real spectral class.
for star in starList:
    c,s,l = guess(star.mass,star.radius,star.temperature,star.age)
    if c not in remnants:
        newguess = c + str(s) + ' ' + l
    else:
        newguess = c
    if star.name != newguess:
        if star.source not in known_bad:
            if c != '':
                print('actual:',star.name,'guessed:',newguess)
                star.report()
            fails += 1
        else:
            ignored += 1

length = len(starList)
remainder = length - ignored
print()
print('Total number of stars:',length)
print('Ignored:',ignored,'(handplaced catalogue stars, stars which aren\'t primary and incomplete entries.)')
print('Remaining stars:',remainder)
successes = remainder - fails
s_percentage = round((100 * (successes / remainder)),1)
print(successes,'succeeded and',fails,'failed from',remainder,';',s_percentage,'% success.')
print()
print('Creating HR and Age / Mass diagrams.')
print()

identifier = str(length)

picsize = (1000,600)
HR = HR_diagram(starList,picsize)
filename = 'HRdiagram' + identifier + '.png'
HR.save(filename)
print('Saved',filename)

picsize = (1000,600)
bounds = (0.9,0.01,14000,130)
AM = AM_diagram(starList,picsize,bounds)
filename = 'AMdiagram' + identifier + '.png'
print('Saved',filename)
AM.save(filename)

print()
print('Completed.')

# --------------
# USER INSTRUCTIONS
#
# Now you will put everything together.
#
# First make sure that your sense and move functions
# work as expected for the test cases provided at the
# bottom of the previous two programming assignments.
# Once you are satisfied, copy your sense and move
# definitions into the robot class on this page, BUT
# now include noise.
#
# A good way to include noise in the sense step is to
# add Gaussian noise, centered at zero with variance
# of self.bearing_noise to each bearing. You can do this
# with the command random.gauss(0, self.bearing_noise)
#
# In the move step, you should make sure that your
# actual steering angle is chosen from a Gaussian
# distribution of steering angles. This distribution
# should be centered at the intended steering angle
# with variance of self.steering_noise.
#
# Feel free to use the included set_noise function.
#
# Please do not modify anything except where indicated
# below.

from __future__ import print_function
from math import *
import random
import Euv.Frame as Frame
import Euv.EuvGtk as Euv
import Euv.Color as Color
import Euv.Shapes as Shapes

# --------
# 
# some top level parameters
#

max_steering_angle = pi / 4.0 # You do not need to use this value, but keep in mind the limitations of a real car.
bearing_noise = 0.1 # Noise parameter: should be included in sense function.
steering_noise = 0.1 # Noise parameter: should be included in move function.
distance_noise = 5.0 # Noise parameter: should be included in move function.

tolerance_xy = 15.0 # Tolerance for localization in the x and y directions.
tolerance_orientation = 0.25 # Tolerance for orientation.


# --------
# 
# the "world" has 4 landmarks.
# the robot's initial coordinates are somewhere in the square
# represented by the landmarks.
#
# NOTE: Landmark coordinates are given in (y, x) form and NOT
# in the traditional (x, y) format!

landmarks  = [[0.0, 100.0], [0.0, 0.0], [100.0, 0.0], [100.0, 100.0]] # position of 4 landmarks in (y, x) format.
world_size = 100.0 # world is NOT cyclic. Robot is allowed to travel "out of bounds"

# ------------------------------------------------
# 
# this is the robot class
#

class robot:

    # --------
    # init: 
    #    creates robot and initializes location/orientation 
    #

    def __init__(self, length = 20.0):
        self.x = random.random() * world_size # initial x position
        self.y = random.random() * world_size # initial y position
        self.orientation = random.random() * 2.0 * pi # initial orientation
        self.length = length # length of robot
        self.bearing_noise  = 0.0 # initialize bearing noise to zero
        self.steering_noise = 0.0 # initialize steering noise to zero
        self.distance_noise = 0.0 # initialize distance noise to zero

    # --------
    # set: 
    #    sets a robot coordinate
    #

    def set(self, new_x, new_y, new_orientation):

        if new_orientation < 0 or new_orientation >= 2 * pi:
            raise ValueError('Orientation must be in [0..2pi]')
        self.x = float(new_x)
        self.y = float(new_y)
        self.orientation = float(new_orientation)

    # --------
    # set_noise: 
    #    sets the noise parameters
    #
    def set_noise(self, new_b_noise, new_s_noise, new_d_noise):
        # makes it possible to change the noise parameters
        # this is often useful in particle filters
        self.bearing_noise  = float(new_b_noise)
        self.steering_noise = float(new_s_noise)
        self.distance_noise = float(new_d_noise)

    # --------
    # measurement_prob
    #    computes the probability of a measurement
    #  

    def measurement_prob(self, measurements):

        # calculate the correct measurement
        predicted_measurements = self.sense(0) # Our sense function took 0 as an argument to switch off noise.


        # compute errors
        error = 1.0
        for i in range(len(measurements)):
            error_bearing = abs(measurements[i] - predicted_measurements[i])
            error_bearing = (error_bearing + pi) % (2.0 * pi) - pi # truncate
            

            # update Gaussian
            try:
                error *= (exp(- (error_bearing ** 2) / (self.bearing_noise ** 2) / 2.0) /  
                          sqrt(2.0 * pi * (self.bearing_noise ** 2)))
            except:
                print("self.bearing_noise = ", self.bearing_noise)
                raise
            

        return error
    
    def __repr__(self): #allows us to print robot attributes.
        return '[x=%.6s y=%.6s orient=%.6s]' % (str(self.x), str(self.y), 
                                                str(self.orientation))
    
    ############# ONLY ADD/MODIFY CODE BELOW HERE ###################
       
    # --------
    # move: 
    #   
    
    # copy your code from the previous exercise
    # and modify it so that it simulates motion noise
    # according to the noise parameters
    #           self.steering_noise
    #           self.distance_noise

    def move(self, motion): # Do not change the name of this function
        # ADD CODE HERE
        alpha = random.gauss(motion[0],self.steering_noise)
        distance = random.gauss(motion[1],self.distance_noise)

        # Turning angle beta
        beta = distance/self.length * tan(alpha)
        straight_cutoff = 0.001
        if beta > straight_cutoff:
            R = distance/beta
            cx = self.x - sin(self.orientation) * R
            cy = self.y + cos(self.orientation) * R
            new_x = cx + sin(self.orientation+beta)*R
            new_y = cy - cos(self.orientation+beta)*R
            new_theta = (self.orientation+beta)%(2*pi)
        else:
            new_x = self.x + distance * cos(self.orientation)
            new_y = self.y + distance * sin(self.orientation)
            new_theta = (self.orientation + beta)%(2*pi)

        result = robot(self.length)
        result.set(new_x,new_y,new_theta)
        result.set_noise(self.bearing_noise, self.steering_noise, self.distance_noise)

        
        return result # make sure your move function returns an instance
                      # of the robot class with the correct coordinates.
                      
    # --------
    # sense: 
    #    

    # copy your code from the previous exercise
    # and modify it so that it simulates bearing noise
    # according to
    #           self.bearing_noise

    def sense(self, use_noise=1): #do not change the name of this function
        Z = []

        # ENTER CODE HERE
        # HINT: You will probably need to use the function atan2()

        for i in range(4):
          ly,lx = landmarks[i]
          bearing = atan2(ly-self.y, lx-self.x)-self.orientation
          if use_noise:
            bearing += random.gauss(0,self.bearing_noise)
          Z.append(bearing%(2*pi))

        return Z #Leave this line here. Return vector Z of 4 bearings.

    ############## ONLY ADD/MODIFY CODE ABOVE HERE ####################

# --------
#
# extract position from a particle set
# 

def get_position(p):
    x = 0.0
    y = 0.0
    orientation = 0.0
    for i in range(len(p)):
        x += p[i].x
        y += p[i].y
        # orientation is tricky because it is cyclic. By normalizing
        # around the first particle we are somewhat more robust to
        # the 0=2pi problem
        orientation += (((p[i].orientation - p[0].orientation + pi) % (2.0 * pi)) 
                        + p[0].orientation - pi)
    return [x / len(p), y / len(p), orientation / len(p)]

# --------
#
# The following code generates the measurements vector
# You can use it to develop your solution.
# 


def generate_ground_truth(motions):

    robots = []
    myrobot = robot()
    myrobot.set_noise(bearing_noise, steering_noise, distance_noise)

    Z = []
    T = len(motions)

    for t in range(T+1):
        Z.append(myrobot.sense())
        robots.append(myrobot)
        if t<T:
            myrobot = myrobot.move(motions[t])
    #print('Robot:    ', myrobot)
    return robots, Z

# --------
#
# The following code prints the measurements associated
# with generate_ground_truth
#

def print_measurements(Z):

    T = len(Z)

    print('measurements = [[%.8s, %.8s, %.8s, %.8s],' %
        (str(Z[0][0]), str(Z[0][1]), str(Z[0][2]), str(Z[0][3])))
    for t in range(1,T-1):
        print('                [%.8s, %.8s, %.8s, %.8s],' %
            (str(Z[t][0]), str(Z[t][1]), str(Z[t][2]), str(Z[t][3])))
    print('                [%.8s, %.8s, %.8s, %.8s]]' %
        (str(Z[T-1][0]), str(Z[T-1][1]), str(Z[T-1][2]), str(Z[T-1][3])))

# --------
#
# The following code checks to see if your particle filter
# localizes the robot to within the desired tolerances
# of the true position. The tolerances are defined at the top.
#

def check_output(final_robot, estimated_position):

    error_x = abs(final_robot.x - estimated_position[0])
    error_y = abs(final_robot.y - estimated_position[1])
    error_orientation = abs(final_robot.orientation - estimated_position[2])
    error_orientation = (error_orientation + pi) % (2.0 * pi) - pi
    correct = error_x < tolerance_xy and error_y < tolerance_xy \
              and error_orientation < tolerance_orientation
    return correct


def show_frame(v,p,robot):
  """Show the current probability and the current robot"""
  f = Frame.Frame()
  for l in landmarks:
    f.add_circle(pos=(l[1],l[0]),
                 color=Color.Color("blue"),
                 radius=3)
  for r in p:
    poly = Shapes.arrow_head_polygon((r.x, r.y),
                                     r.orientation,
                                     scale=0.5)
    f.add_polygons([poly],
                   color=Color.Color("red"),
                   alpha=0.2)
  poly = Shapes.arrow_head_polygon((robot.x, robot.y),
                                   robot.orientation,
                                   scale=0.5
                                   )
  f.add_polygons([poly],
                 color=Color.Color("black"),
                 alpha=0.9)
  v.add_frame(f)


def particle_filter(motions, measurements, final_robot,N=500): # I know it's tempting, but don't change N!
    # --------
    #
    # Make particles
    # 

    v = Euv.Viewer(size=(600,600),
                   view_port_center = (50,50),
                   view_port_width = 300,
                   )

    p = []
    for i in range(N):
        r = robot()
        r.set_noise(bearing_noise, steering_noise, distance_noise)
        p.append(r)

    # --------
    #
    # Update particles
    #     

    for t in range(len(motions)):
        show_frame(v,p,final_robot[t])
    
        # motion update (prediction)
        p2 = []
        for i in range(N):
            p2.append(p[i].move(motions[t]))
        p = p2

        # measurement update
        w = []
        for i in range(N):
            w.append(p[i].measurement_prob(measurements[t]))

        # resampling
        p3 = []
        index = int(random.random() * N)
        beta = 0.0
        mw = max(w)
        for i in range(N):
            beta += random.random() * 2.0 * mw
            while beta > w[index]:
                beta -= w[index]
                index = (index + 1) % N
            p3.append(p[index])
        p = p3
        show_frame(v,p,final_robot[t])
    
    # Wait for GUI to finish
    v.wait()
    
    return get_position(p)

## IMPORTANT: You may uncomment the test cases below to test your code.
## But when you submit this code, your test cases MUST be commented
## out.
##
## You can test whether your particle filter works using the
## function check_output (see test case 2). We will be using a similar
## function. Note: Even for a well-implemented particle filter this
## function occasionally returns False. This is because a particle
## filter is a randomized algorithm. We will be testing your code
## multiple times. Make sure check_output returns True at least 80%
## of the time.


 
## --------
## TEST CASES:
## 
##1) Calling the particle_filter function with the following
##    motions and measurements should return a [x,y,orientation]
##    vector near [x=93.476 y=75.186 orient=5.2664], that is, the
##    robot's true location.
##
##motions = [[2. * pi / 10, 20.] for row in range(8)]
##measurements = [[4.746936, 3.859782, 3.045217, 2.045506],
##                [3.510067, 2.916300, 2.146394, 1.598332],
##                [2.972469, 2.407489, 1.588474, 1.611094],
##                [1.906178, 1.193329, 0.619356, 0.807930],
##                [1.352825, 0.662233, 0.144927, 0.799090],
##                [0.856150, 0.214590, 5.651497, 1.062401],
##                [0.194460, 5.660382, 4.761072, 2.471682],
##                [5.717342, 4.736780, 3.909599, 2.342536]]
##
##print particle_filter(motions, measurements)
##
## 2) You can generate your own test cases by generating
##    measurements using the generate_ground_truth function.
##    It will print the robot's last location when calling it.
##
##
number_of_iterations = 25
motions = [[2. * pi / 20, 12.] for row in range(number_of_iterations)]

robots, measurements = generate_ground_truth(motions)
estimated_position = particle_filter(motions, measurements, robots)
print_measurements(measurements)
print('Ground truth:    ', robots[-1])
print('Particle filter: ', estimated_position)
print('Code check:      ', check_output(robots[-1], estimated_position))

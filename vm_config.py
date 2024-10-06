# Import necessary modules from gem5 components
import m5
from m5.objects import *
from m5.util import addToPath

# Load common scripts
addToPath('../common')
import Options
import Simulation
import CacheConfig
import CpuConfig

# Parse options
parser = Options.get_standard_parser()
(opts, args) = parser.parse_args()

# Create a system: basic setup
system = System()

system.clk_domain = SrcClockDomain()
system.clk_domain.clock = '1GHz'
system.clk_domain.voltage_domain = VoltageDomain()

system.mem_mode = 'timing'  # Use timing mode for detailed simulation
system.mem_ranges = [AddrRange('512MB')]  # Memory size

# Create a CPU
system.cpu = TimingSimpleCPU()

# Memory system setup
system.membus = SystemXBar()  # System crossbar

# Setup virtual memory page size
system.cpu.createInterruptController()
system.cpu.interrupts[0].pio = system.membus.master
system.cpu.interrupts[0].int_master = system.membus.slave
system.cpu.interrupts[0].int_slave = system.membus.master

# TLB configurations
system.cpu.itb.size = 16  # Instruction TLB size
system.cpu.dtb.size = 16  # Data TLB size

# Setup cache
system.cpu.icache = Cache(size='32kB', assoc=2, block_size=64)
system.cpu.dcache = Cache(size='32kB', assoc=2, block_size=64)
system.cpu.icache.connectBus(system.membus)
system.cpu.dcache.connectBus(system.membus)

# Setup L2 cache
system.l2cache = L2Cache(size='256kB', assoc=8, block_size=64)
system.l2cache.connectCPUSideBus(system.membus)

# Connect the system up with a memory controller
system.mem_ctrl = DDR3_1600_8x8()
system.mem_ctrl.range = system.mem_ranges[0]
system.mem_ctrl.port = system.membus.master

# Setup the system simulation
root = Root(full_system = False, system = system)
m5.instantiate()

print("Beginning simulation!")
exit_event = m5.simulate()
print('Exiting @ tick %i because %s' % (m5.curTick(), exit_event.getCause()))

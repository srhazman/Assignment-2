from mmu import MMU

# ClockMMU implements the Clock page replacement algorithm
class ClockMMU(MMU):
    def __init__(self, frames):
        self.frames = frames
        self.memory = []  # Each entry: {'page': int, 'ref': bool, 'dirty': bool}
        self.pointer = 0  # Points to the next frame to check for replacement
        self.disk_reads = 0
        self.disk_writes = 0
        self.page_faults = 0
        self.debug_mode = False

    def set_debug(self):
        # Enable debug mode for verbose output
        self.debug_mode = True

    def reset_debug(self):
        # Disable debug mode
        self.debug_mode = False

    def read_memory(self, page_number):
        # Handle a memory read operation
        for entry in self.memory:
            if entry['page'] == page_number:
                entry['ref'] = True  # Set reference bit on hit
                if self.debug_mode:
                    print(f"Read hit: {page_number}")
                return
        # Page fault: page not found
        self.page_faults += 1
        self.disk_reads += 1
        # Page replacement logic (Clock algorithm)
        if len(self.memory) < self.frames:
            # Free frame available, just add the page
            self.memory.append({'page': page_number, 'ref': True, 'dirty': False})
        else:
            # No free frame, use Clock algorithm to replace a page
            while True:
                entry = self.memory[self.pointer]
                if not entry['ref']:
                    # Replace this page
                    if entry['dirty']:
                        self.disk_writes += 1  # Write back if dirty
                    self.memory[self.pointer] = {'page': page_number, 'ref': True, 'dirty': False}
                    self.pointer = (self.pointer + 1) % self.frames
                    break
                else:
                    # Give second chance, clear reference bit
                    entry['ref'] = False
                    self.pointer = (self.pointer + 1) % self.frames

    def write_memory(self, page_number):
        # Handle a memory write operation
        for entry in self.memory:
            if entry['page'] == page_number:
                entry['ref'] = True  # Set reference bit on hit
                entry['dirty'] = True  # Mark as dirty
                if self.debug_mode:
                    print(f"Write hit: {page_number}")
                return
        # Page fault: page not found
        self.page_faults += 1
        self.disk_reads += 1
        # Page replacement logic (Clock algorithm)
        if len(self.memory) < self.frames:
            # Free frame available, just add the page
            self.memory.append({'page': page_number, 'ref': True, 'dirty': True})
        else:
            # No free frame, use Clock algorithm to replace a page
            while True:
                entry = self.memory[self.pointer]
                if not entry['ref']:
                    # Replace this page
                    if entry['dirty']:
                        self.disk_writes += 1  # Write back if dirty
                    self.memory[self.pointer] = {'page': page_number, 'ref': True, 'dirty': True}
                    self.pointer = (self.pointer + 1) % self.frames
                    break
                else:
                    # Give second chance, clear reference bit
                    entry['ref'] = False
                    self.pointer = (self.pointer + 1) % self.frames

    def get_total_disk_reads(self):
        return self.disk_reads

    def get_total_disk_writes(self):
        return self.disk_writes

    def get_total_page_faults(self):
        return self.page_faults

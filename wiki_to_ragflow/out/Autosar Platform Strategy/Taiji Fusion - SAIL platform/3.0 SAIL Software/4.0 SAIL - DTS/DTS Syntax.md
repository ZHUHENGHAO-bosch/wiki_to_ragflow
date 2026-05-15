# DTS Syntax

> Source: /spaces/CARSFW/pages/4938201931/DTS+Syntax
> Last modified: 2024-10-31T09:31:54.000+01:00

---

Device Tree Source (DTS) syntax is used to describe hardware layouts for systems, particularly in embedded Linux environments. DTS files are written in a hierarchical, tree-like structure that represents the components and properties of a device. They are compiled into Device Tree Blobs (DTBs), which the Linux kernel can then read to understand hardware configurations without needing specific drivers hard-coded.

## Key Elements of DTS Syntax

### Nodes

- Represent devices or components and are organized in a nested tree structure.
- Each node begins with a name (e.g., `cpu@0`, `memory`, `gpio`) and is defined with curly braces `{}`
- Nodes often have labels that can be used for reference, prefixed by a backslash `&` in other parts of the DTS file.

```
   cpu@0 {         // Node name with unit address
       compatible = "arm,cortex-a7";  // Property
       reg = <0x0>;
   };
```

### Properties

- Define attributes of nodes, given as key-value pairs (e.g., `compatible = "arm,cortex-a7";`).
- Properties can be single values, lists, or even empty (indicating a boolean true).

```
   memory {
       device_type = "memory";
       reg = <0x80000000 0x40000000>;  // Memory address and size
   };
```

### Hierarchy and Nesting

- Nodes can be nested within other nodes, reflecting the hardware layout hierarchy.
- For example, a CPU node might contain nodes for specific registers or peripherals within that CPU.

```
  soc {                     // Top-level node
       uart@1000 {           // Nested UART node
           compatible = "ns16550a";
           reg = <0x1000 0x100>;
       };
   };
```

### References and Labels

- Labels can be assigned to nodes or properties for easy reference.
- Labels are followed by a colon, e.g., `uart: uart@1000`.

```
&uart {                   // Referencing the uart label
       status = "okay";
   };
```

### Includes and Overlays

- `#include` statements are used to import additional files or headers.
- Overlays can modify base device trees by adding, modifying, or deleting nodes and properties.

## Example DTS File Structure

Here's a simple DTS snippet that shows these elements in action:

```
/dts-v1/;
/ {
    compatible = "my_board";

    memory {
        device_type = "memory";
        reg = <0x80000000 0x40000000>;  // Start address and size
    };

    soc {
        compatible = "simple-bus";
        #address-cells = <1>;
        #size-cells = <1>;

        uart@1000 {
            compatible = "ns16550a";
            reg = <0x1000 0x100>;
            interrupt-parent = <&intc>;
            interrupts = <5>;
        };

        gpio@2000 {
            compatible = "my_gpio";
            reg = <0x2000 0x100>;
        };
    };
};
```

## Common DTS Properties

- compatible : Identifies the type of device.
- reg : Specifies the address and size of a device in the memory map.
- status : Specifies if a device is active ( okay ) or disabled ( disabled ).
- interrupts : Defines interrupt numbers for devices requiring interrupts.

## Compilation to DTB

The DTS files are compiled to a binary form, Device Tree Blob (DTB), using the dtc.exe(Device Tree Compiler) tool:

```
dtc -I dts -O dtb -o my_device_tree.dtb my_device_tree.dts
```

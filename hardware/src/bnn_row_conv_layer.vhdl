-- Row-parallel BNN convolution layer

library IEEE;
use IEEE.std_logic_1164.all;
use IEEE.numeric_std.all;


entity bnn_row_conv_layer is
    generic (
        COUNT_IN    : integer; -- Number of input images
        COUNT_OUT   : integer; -- Number of kernels per image
        OUTPUT_WIDTH : integer;
        INPUT_COLS  : integer;
        KERNEL_COLS : integer;
        KERNEL_ROWS : integer
    );
    port (
        -- System
        clk         : in  std_logic;
        reset       : in  std_logic;

        -- Weight configuration
        w_en        : in  std_logic; -- enable shifting
        w_in        : in  std_logic; -- input
        w_out       : out std_logic; -- output/passthrough

        -- Input data
        row_in      : in  std_logic_vector(COUNT_IN*INPUT_COLS-1 downto 0);
        ready       : in  std_logic;

        -- Output data
        row_out     : out std_logic_vector(COUNT_IN*COUNT_OUT*(INPUT_COLS-KERNEL_COLS+1)*OUTPUT_WIDTH-1 downto 0);
        done        : out std_logic
    );
end entity;


architecture struct of bnn_row_conv_layer is

    constant ROW_OUT_WIDTH : integer := (INPUT_COLS-KERNEL_COLS+1)*OUTPUT_WIDTH;

    signal w_pass : std_logic_vector(0 to COUNT_IN*(COUNT_OUT+1)-1);
    signal done_s : std_logic_vector(0 to COUNT_IN*COUNT_OUT-1);

begin

bnn_row_conv_gen_gen: for IO in 0 to COUNT_OUT-1 generate
    bnn_row_conv_gen: for II in 0 to COUNT_IN-1 generate
        bnn_row_conv_inst: entity work.bnn_row_conv
            generic map (
                OUTPUT_WIDTH => OUTPUT_WIDTH,
                INPUT_COLS  => INPUT_COLS,
                KERNEL_COLS => KERNEL_COLS,
                KERNEL_ROWS => KERNEL_ROWS
            )
            port map (
                clk         => clk,
                reset       => reset,

                w_en        => w_en,
                w_in        => w_pass(IO*COUNT_IN+II),
                w_out       => w_pass((IO+1)*COUNT_IN+II),

                row_in      => row_in((II+1)*INPUT_COLS-1 downto II*INPUT_COLS),
                ready       => ready,

                row_out     => row_out((IO*COUNT_IN+II+1)*ROW_OUT_WIDTH-1 downto (IO*COUNT_IN+II)*ROW_OUT_WIDTH),
                done        => done_s(IO*COUNT_IN+II)
            );
    end generate;
end generate;


w_in_gen: for I in 0 to COUNT_IN-1 generate
        w_pass(I) <= w_in;
    end generate;

    w_out <= w_pass(COUNT_IN*COUNT_OUT);

    done <= done_s(0);

end architecture;

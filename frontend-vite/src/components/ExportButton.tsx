import { Button, Menu, MenuButton, MenuList, MenuItem, Icon } from '@chakra-ui/react';
import { motion } from 'framer-motion';
import { FiDownload, FiFileText, FiFile } from 'react-icons/fi';

const MotionButton = motion(Button);

interface ExportButtonProps {
  onExportPDF?: () => void;
  onExportCSV?: () => void;
  disabled?: boolean;
}

export default function ExportButton({ onExportPDF, onExportCSV, disabled = false }: ExportButtonProps) {
  return (
    <Menu>
      <MenuButton
        as={MotionButton}
        leftIcon={<FiDownload />}
        bg="linear-gradient(135deg, #EF0107 0%, #9C0D0F 100%)"
        color="white"
        size="sm"
        isDisabled={disabled}
        whileHover={{ scale: 1.05 }}
        whileTap={{ scale: 0.95 }}
        _hover={{
          bg: 'linear-gradient(135deg, #FF4655 0%, #EF0107 100%)',
          boxShadow: '0 4px 12px rgba(239, 1, 7, 0.4)',
        }}
        _active={{
          bg: 'linear-gradient(135deg, #9C0D0F 0%, #7A0A0C 100%)',
        }}
        transition="all 0.3s ease"
      >
        Export
      </MenuButton>
      <MenuList
        bg="rgba(255, 255, 255, 0.05)"
        backdropFilter="blur(10px)"
        border="1px solid rgba(255, 255, 255, 0.1)"
        boxShadow="0 8px 32px rgba(0, 0, 0, 0.3)"
      >
        {onExportPDF && (
          <MenuItem
            icon={<Icon as={FiFileText} />}
            onClick={onExportPDF}
            bg="transparent"
            color="white"
            _hover={{
              bg: 'rgba(239, 1, 7, 0.2)',
            }}
          >
            Export as PDF
          </MenuItem>
        )}
        {onExportCSV && (
          <MenuItem
            icon={<Icon as={FiFile} />}
            onClick={onExportCSV}
            bg="transparent"
            color="white"
            _hover={{
              bg: 'rgba(239, 1, 7, 0.2)',
            }}
          >
            Export as CSV
          </MenuItem>
        )}
      </MenuList>
    </Menu>
  );
}
